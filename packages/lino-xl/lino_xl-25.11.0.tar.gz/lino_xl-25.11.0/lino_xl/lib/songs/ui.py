# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from lino.modlib.users.mixins import My
from lino.core import constants
from lino_xl.lib.contacts.roles import ContactsStaff, ContactsUser
from .choicelists import AuthorRoles


class SongTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'songs.SongType'
    column_names = 'designation *'
    detail_layout = """id designation
    SongsByType
    """


class SongDetail(dd.DetailLayout):
    main = "general scores more"

    general = dd.Panel("""
    title:60 language:10
    subtitle parent
    body
    """, label=_("General"))

    more = dd.Panel("""
    id user group private song_type
    publishing_state pub_date
    source license copyright_owner year_published
    songs.ComposersBySong songs.AuthorsBySong topics.TagsByOwner songs.SongsByParent
    """, label=_("More"))

    scores = dd.Panel("""
    scores_tempo scores_preamble scores_line_width other_font
    scores_lyrics scores_chords
    scores_soprano scores_alto scores_tenor scores_bass
    scores_errors
    """, label=_("Scores"))


class Songs(dd.Table):
    model = "songs.Song"
    column_names = 'id title language source *'
    detail_layout = "songs.SongDetail"
    # params_panel_pos = 'left'
    # params_layout = """
    # group
    # user
    # author
    # mentor
    # """


class SongsByType(Songs):
    master_key = 'song_type'


class SongsByGroup(Songs):
    master_key = 'group'


class SongsByParent(Songs):
    label = _("Derived songs")
    master_key = 'parent'


class MySongs(My, Songs):
    required_roles = dd.login_required(ContactsUser)
    # label = _("My entries")


class LatestSongs(Songs):
    required_roles = set()  # also for anonymous
    label = _("Latest songs")
    column_names = "pub_date title user *"
    order_by = ["-pub_date"]
    filter = dd.Q(pub_date__isnull=False)
    # default_display_modes = {None: constants.DISPLAY_MODE_LIST}
    # editable = False
    insert_layout = None  # disable the (+) button but permit editing
    default_display_modes = {
        None: constants.DISPLAY_MODE_LIST}


class AuthorCasts(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'songs.AuthorCast'


class CastsByAuthor(AuthorCasts):
    master_key = 'author'
    required_roles = dd.login_required()
    column_names = "song role *"
    # required_roles = dd.login_required(ContactsUser)
    # details_of_master_template = _("%(details)s")
    # insert_layout = """
    # song
    # role
    # """
    obvious_fields = {'author'}
    # default_display_modes = {  # temporary workaround
    #     None: constants.DISPLAY_MODE_SUMMARY}


class CastsBySong(AuthorCasts):
    master_key = 'song'
    required_roles = dd.login_required(ContactsUser)
    # details_of_master_template = _("%(details)s")
    insert_layout = """
    author
    role
    """
    obvious_fields = {'song', 'role'}
    default_display_modes = {  # temporary workaround
        None: constants.DISPLAY_MODE_SUMMARY}


class AuthorsBySong(CastsBySong):
    label = _("Authors")
    known_values = dict(role=AuthorRoles.author)
    insert_layout = """
    author
    """


class ComposersBySong(CastsBySong):
    label = _("Composers")
    known_values = dict(role=AuthorRoles.composer)
    insert_layout = """
    author
    """
