"""[WIP] Community op constructor"""

import json
from typing import Union

from hive.community.roles import PERMISSIONS, is_permitted
from hive.indexer.community import is_community
#from steem.account import Account


class Community:
    """ Community is an extension of steem.commit.Commit class. It allows you to construct
    various community related `custom_json` operations, and commit them onto the blockchain.

    Args:
        community_name (str): Community to operate in.
        account_name (str): Account to perform actions with.
    """

    _id = 'com.steemit.community'
    _roles = PERMISSIONS.keys()
    _valid_settings = ['title', 'about', 'description', 'language', 'is_nsfw']

    def __init__(self, community_name: str, account_name: str):
        self.community = community_name
        self.account = account_name

    def create(self, community_type: str = 'public', admins: Union[str, list] = None):
        """ Create a new community.

        This method will upgrade an existing STEEM account into a new community.

        Args:
            community_type: Can be **public** (default) or **restricted**.
            admins: list of users who will be community Admins.
             If left empty, the owner will be assigned as a single admin.
        """
        # validate account and community name
        #Account(self.account)
        assert self.community == self.account, 'Account name and community name need to be the same'

        if is_community(self.community):
            raise NameError('community %s already exists.' % self.community)

        if isinstance(admins, str):
            admins = [admins]
        if not admins:
            admins = [self.community]

        op = self._op(action='create',
                      type=community_type,
                      admins=admins)
        return self._commit(op)

    def update_settings(self, **settings):
        """ Update community settings / metadata. """
        # sanitize the settings to valid keys
        settings = {k: v for k, v in settings.items() if k in self._valid_settings}
        assert self._has_permissions('update_settings'), 'Insufficient Community Permissions'
        op = self._op(action='update_settings', settings=settings)
        return self._commit(op)

    def add_users(self, account_names: Union[str, list], role: str):
        """ Add user to the community in the specified role.

        Args:
            account_names (str, list): accounts to add to the community.
            role (str): Roles to apply. Can be admin, moderator or poster.

        """
        return self._add_or_remove_users(account_names, role, 'add')

    def remove_users(self, account_names: Union[str, list], role: str):
        """ Opposite of `add_user`. """
        return self._add_or_remove_users(account_names, role, 'remove')

    def _add_or_remove_users(self, account_names: Union[str, list], role: str, action: str):
        """ Implementation for adding/removing users to communities under various roles. """
        if isinstance(account_names, str):
            account_names = [account_names]

        if role not in self._roles:
            raise ValueError('Invalid role `%s`. options: %s' % (role, ', '.join(self._roles)))

        action_name = '{0}_{1}s'.format(action, role)
        assert self._has_permissions(action_name), 'Insufficient Community Permissions'
        op = self._op(action=action_name, accounts=account_names)
        return self._commit(op)

    def set_user_title(self, account_name: str, title: str):
        """ Set a title for given user. """
        # todo: check permissions.
        # can you asssign title to self?
        # can mod/admin assign title to someone else?
        op = self._op(action='set_user_title', account=account_name, title=title)
        return self._commit(op)

    def mute_user(self, account_name: str):
        """ Mute user """
        assert self._has_permissions('mute_user'), 'Insufficient Community Permissions'
        op = self._op(action='mute_user', account=account_name)
        return self._commit(op)

    def unmute_user(self, account_name: str):
        """ Un-Mute user """
        assert self._has_permissions('unmute_user'), 'Insufficient Community Permissions'
        op = self._op(action='unmute_user', account=account_name)
        return self._commit(op)

    def mute_post(self, author: str, permlink: str, notes: str):
        """ Mute post """
        assert self._has_permissions('mute_post'), 'Insufficient Community Permissions'
        op = self._op(action='mute_post', author=author, permlink=permlink, notes=notes)
        return self._commit(op)

    def unmute_post(self, author: str, permlink: str, notes: str):
        """ Un-Mute post """
        assert self._has_permissions('unmute_post'), 'Insufficient Community Permissions'
        op = self._op(action='unmute_post', author=author, permlink=permlink, notes=notes)
        return self._commit(op)

    def pin_post(self, author: str, permlink: str):
        """ Pin post """
        assert self._has_permissions('pin_post'), 'Insufficient Community Permissions'
        op = self._op(action='pin_post', author=author, permlink=permlink)
        return self._commit(op)

    def unpin_post(self, author: str, permlink: str):
        """ Un-Pin post """
        assert self._has_permissions('unpin_post'), 'Insufficient Community Permissions'
        op = self._op(action='unpin_post', author=author, permlink=permlink)
        return self._commit(op)

    def flag_post(self, author: str, permlink: str, comment: str):
        """ Flag post """
        assert self._has_permissions('flag_post'), 'Insufficient Community Permissions'
        op = self._op(action='flag_post', author=author, permlink=permlink, comment=comment)
        return self._commit(op)

    def _commit(self, community_op: Union[list, str]):
        """ Construct and commit a community *custom_json* operation to the blockchain. """
        if isinstance(community_op, str):
            community_op = json.loads(community_op)

        op = {'json': community_op,
              'required_auths': [],
              'required_posting_auths': [self.account],
              'id': Community._id}
        return op

    def _op(self, action: str, **params):
        """ Generate a standard data structure for community *custom_json* operations. """
        return [action, {
            'community': self.community,
            **params
        }]

    def _has_permissions(self, action: str, account_name=None) -> bool:
        """ Check if this account has the right to perform this action within the community.
        Should be called as helper in most methods.
        """
        if not account_name:
            account_name = self.account

        return is_permitted(account_name, self.community, action)


if __name__ == '__main__':
    pass
