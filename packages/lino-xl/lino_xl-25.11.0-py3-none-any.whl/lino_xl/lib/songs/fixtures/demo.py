# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from textwrap import dedent
from lino.modlib.publisher.choicelists import PublishingStates, SpecialPages
from lino.utils.mldbc import babel_named as named
from lino.utils.soup import MORE_MARKER
from lino.api import dd, rt, _
from lino.utils.cycler import Cycler
from lino.utils.instantiator import get_or_create
# from lino.modlib.publisher.models import create_special_pages


User = rt.models.users.User
Place = rt.models.countries.Place
Language = rt.models.languages.Language
Country = rt.models.countries.Country
Source = rt.models.sources.Source
License = rt.models.sources.License
Author = rt.models.sources.Author
Song = rt.models.songs.Song
SongType = rt.models.songs.SongType
Upload = rt.models.uploads.Upload
# if dd.plugins.publisher.with_trees:
#     Tree = rt.models.publisher.Tree
Page = rt.models.publisher.Page
PageItem = rt.models.publisher.PageItem
Topic = rt.models.topics.Topic
Tag = rt.models.topics.Tag
Group = rt.models.groups.Group
Company = rt.models.contacts.Company
AuthorCast = rt.models.songs.AuthorCast
AuthorRoles = rt.models.songs.AuthorRoles


def song_type(name):
    return SongType(**dd.str2kw('designation', name))


def plain2rich(s):
    s = s.strip()
    if s.startswith("<"):
        return s
    s = "".join(["<p>{}</p>".format(p) for p in s.split("\n\n")])
    # return s.replace("\n", "<br/>")
    return s


# SONGS_FROM_TAIZE = []
#
#
# def add(title, **values):
#     SONGS_FROM_TAIZE.append(dict(title=title, **values))
#
#
# add("Tule, tule, Jumala vaim",
#     subtitle="Przybądź Duchu Boży",
#     scores_line_width=r'180\mm',
#     other_font=True,
#     composers=["Taizé"],
#     scores_tempo='4. = 49',
#     scores_preamble=r"\key g \major \time 6/8",
#     scores_lyrics=r"""
#     - Tu- le, tu- le Ju- ma- la vaim, tu- le, tu- le Pü- ha Vaim ja uu- en- da maa- il- ma pa- le, ja uu- en- da maa- il- ma pa- le!
#     - Przy- bądź Du- chu Bo- _ _ ży, przy- bądź Du- chu Świę- _ ty i od- nów o- bli- _ cze zie- mi, i od- nów o- bli- _ cze zie- mi
#     """,
#     scores_soprano="""
#     g4 a8 b( a) g | fis8 e d e4.  |
#     b'4 c8 d( c) b | b8( c) b a4 a8  |
#     a8 a g a8 a b8 | c4. b4 b8 |
#     g8 a b a8 a8 a8 | g4. fis
#     """,
#     scores_alto="""
#     e4 fis8 g( fis) e  | d8 e b b4.  |
#     e4 g8 a4 g8  | g8( a) g fis4 fis8  |
#     e8 e d e fis g | g4( a8) g4 fis8 |
#     e8 e b d8 d fis | e4. dis
#     """,
#     scores_tenor="""
#     b4 d8 d4 b8 | b4. g | g4 g8 d'4 d8 | d4. d4 d8 |
#     a8 a b c4 d8 | e4( d8) d4 d8 | b8 a g a4 d8 | b( g a) b4.
#     """,
#     scores_bass="""
#     e4 d8 g4 g8 | b,4. e | g4 e8 fis4 g8 | d4. d4 d8 |
#     c8 c b a4 g8 | e'4( fis8) g4 b,8 | e8 e e fis4 d8 | e4. b4.
#     """,
#     language="pol")


def update(obj, **kwargs):
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


USERS = Cycler(User.objects.all())
# if dd.plugins.publisher.with_trees:
#     TREES = Cycler(Tree.objects.all())
# persons = rt.models.contacts.Person.objects.all()
# MENTORS = Cycler(persons[:2])
# AUTHORS = Cycler(persons[2:])
# assert len(MENTORS) > 0


def objects():

    # FR = Country.objects.get(isocode="FR")
    # place = Place(name="Taizé", country=FR)
    # yield place
    # taize = Company(
    #     name="Ateliers et Presses de Taizé",
    #     street="Communauté de Taizé",
    #     zip_code="71250", city=place,
    #     url="https://www.taize.fr")
    # # yield comp
    # # taize = Source(copyright_owner=comp, title="Songs from Taizé")
    # yield taize

    EE = Country.objects.get(isocode="EE")
    tallinn = Place.objects.get(name="Tallinn", country=EE)
    eelk = Company(
        name="Eesti Evangeelne Luterlik Kirik", street="Kiriku Plats 3",
        city=tallinn, country=EE, url="https://www.eelk.ee")
    yield eelk
    klpr = Source(copyright_owner=eelk, title="KLPR")
    yield klpr

    gotteslob = Source(title="Gotteslob")
    yield gotteslob

    # by_nd = License.objects.get(ref="cc by-nd")
    pd = License.objects.get(ref="pd")

    # yield (taize_type := song_type(_("Taizé")))
    songs = named(Group, _("Songs"), private=False)
    yield songs

    # ENTRYTYPES = Cycler(SongType.objects.all())
    # GROUPS = Cycler(Group.objects.all())
    # TOPICS = Cycler(Topic.objects.all())

    def song(
            authors=None, composers=None, translators=None, language=None,
            **kwargs):
        e = Song(**kwargs)
        user = USERS.pop()
        e.group = songs
        if language is not None:
            e.language = Language.objects.get(pk=language)
        # if dd.plugins.publisher.with_trees:
        #     e.publisher_tree = TREES.pop()
        # e.group = e.publisher_tree.group
        e.user = user
        e.publishing_state = PublishingStates.published
        e.pub_date = dd.today()
        # yield AuthorCast(entry=e, role=AuthorRoles.author, partner=AUTHORS.pop())
        # if e.id % 2:
        #     yield AuthorCast(entry=e, role=AuthorRoles.translator, partner=AUTHORS.pop())
        # yield AuthorCast(entry=e, role=AuthorRoles.composer, partner=MENTORS.pop())
        yield e

        def add_authors(role, lst):
            if lst is not None:
                for x in lst:
                    a = get_or_create(Author, last_name=x)
                    yield a
                    yield AuthorCast(song=e, role=role, author=a)
                    # TODO: use lino.mixins.human.parse_name() to parse name

        yield add_authors(AuthorRoles.composer, composers)
        yield add_authors(AuthorRoles.author, authors)
        yield add_authors(AuthorRoles.translator, translators)

        e.scores_errors = e.build_lilypond()
        yield e

    # for kw in SONGS_FROM_TAIZE:
    #     yield song(copyright_owner=taize, license=by_nd, group=songs, **kw)

    yield song(
        title="Ligidal on Jumal",
        source=klpr,
        license=pd,
        language="est",
        scores_line_width=r'180\mm',
        # scores_tempo='4. = 49',
        scores_preamble=r"\key f \major \time 4/4",
        scores_soprano=r"""
        \repeat volta 2 {
        a4 a a a | g2 g | f4 f f f | e2 e |
        d4 d c f | g a g2 | f2 r
        }
        a4 a bes2 | g4 g a2 | c4 c bes a | g2 a | c4 c bes a | g2 f
        """,
        scores_lyrics=dedent(r"""
        << {
        Li- gi- dal on Ju- mal!
        Te- da kum- mar- da- gem,
        Te- ma et- te pal- ves tul- gem!
        } \new Lyrics { \set associatedVoice = "soprano"
        Me- ie kes- kel Ju- mal!
        Vaik- selt sü- da seis- ku,
        Te- ma ees end a- lan- da- gu.
        } >>
        Tun- nis- ta, aus- ta ka
        Te- ma ni- me kii- tes,
        sil- mi ma- ha hei- tes.
        """),
        body=plain2rich("""
        1. Ligidal on Jumal!
        Teda kummardagem,
        Tema ette palves tulgem!
        Meie keskel Jumal!
        Vaikselt süda seisku,
        Tema ees end alandagu.
        Tunnista, austa ka
        Tema nime kiites,
        silmi maha heites.

        2. Ligidal on Jumal!
        Keerubidki kiitvad,
        seeravid ka maha heitvad.
        Püha, püha, püha!
        Inglikoorid laulvad,
        au ja kiitust Talle andvad.
        Armuga kuule Sa,
        Issand, meie hääli,
        Sinu rahva keeli!

        3. Minu sisse tule,
        Vaim, ja tee mind pühaks,
        Taevaisa pühaks kojaks.
        Ei Sa ole kaugel!
        Armu anna mulle,
        südame siis annan Sulle!
        Valvates, paludes
        hing Sind tunda saagu
        ja Sind kummardagu!
        """),
        authors=["Gerhard Tersteegen, 1697-1769"],
        translators=["Carl Peter Ludwig Maurach, 1824-1900"],
        composers=["Joachim Neander, 1650-1680"])

    yield song(
        title="Kes Jumalat nii laseb teha",
        source=klpr,
        license=pd,
        language="est",
        composers=["Georg Neumark, 1621-1681"],
        scores_line_width=r'180\mm',
        scores_preamble=r"\key as \major \time 4/4 \partial 4",
        scores_soprano=r"""
        \repeat volta 2 {
        c,4 | f g as g | f g es c |
        r | es es des | c f f e | f2.
        }
        g4 | as bes c c | bes bes as \breathe c | bes as g f | as g f \bar "||"
                """,
        scores_lyrics=dedent(r"""
        <<
            {
        Kes Ju- ma- lat nii la- seb te- ha,
        kui Te- ma tun- neb ü- le- valt,
            }
            \new Lyrics {
                \set associatedVoice = "soprano"
        ei Ju- mal te- mast ära lä- he,
        ehk te- mal küll on hä- da kä- es;
            }
            >>
        siis si- na us- ku tun- nis- tad,
        kui hä- das u- sud Ju- ma- lat.
        """),
        body=plain2rich("""
        1. Kes Jumalat nii laseb teha,
        kui Tema tunneb ülevalt,
        ei Jumal temast ära lähe,
        ehk temal küll on häda käes;
        siis sina usku tunnistad,
        kui hädas usud Jumalat.

        2. Mis on sul suurest murest abi?
        Mis kasu annab kurvastus?
        Sa läed küll vanaks mure läbi,
        ei lõpe sinu viletsus.
        Kui sina liialt muretsed,
        siis oma vaeva kasvatad.

        3. Kõik olgu nii kui Jumal tahab,
        kes kõige asja tegija;
        kuis Tema sinu osa jagab,
        nii pead sa rahul olema.
        Küll Jumal teab nii selgesti,
        mis tuleb tarvis kõigile.

        4. See Jumal, kes meid kurvastanud,
        võib peagi anda rõõmu ka,
        kui muretund on mööda läinud,
        siis tuleb Tema abiga:
        kust veel su meel ei mõtlegi,
        sealt tuleb abi sinule.

        5. Siis viimaks head nõu kuulda võta:
        tee tööd ja palu Jumalat!
        Ja lauldes Talle au sa anna
        ka siis, kui kurja kannatad.
        Kes Jumalast ei tagane,
        ei Jumal seda unusta.
        """))

    yield song(
        title="Wer nur den lieben Gott lässt walten",
        source=gotteslob,
        license=pd,
        language="ger",
        composers=["Georg Neumark, 1657", "Johann Sebastian Bach, 1685-1750"],
        scores_line_width=r'180\mm',
        scores_preamble=r"\key bes \major \time 4/4 \partial 4",
        scores_soprano=r"""
        \repeat volta 2 {
        d4 | g a bes a | g a8( g) fis4 d |
        r | f f es | d g g fis | g2 r4
        }
        a4 | bes c d d | c4. bes8 bes4 \breathe
        d | c bes a g8( a) | bes4 a g \bar "||"
                """,
        scores_lyrics=dedent(r"""
        << {
          Wer nur den lie- ben Gott lässt wal- ten
          und hof- fet auf ihn al- le Zeit,
        } \new Lyrics {
          \set associatedVoice = "soprano"
          den wird er wun- der bar er-hal- ten
          in al- ler Not und Trau- rig- keit.
        } >>
        Wer Gott, dem Al- ler- höchs- ten, traut,
        der hat auf kei- nen Sand ge- baut.
        """),
        body=plain2rich("""
        1. Wer nur den lieben Gott lässt walten
        und hoffet auf ihn allezeit,
        den wird er wunderbar erhalten
        in aller Not und Traurigkeit.
        Wer Gott, dem Allerhöchsten, traut,
        der hat auf keinen Sand gebaut.

        2. Was helfen uns die schweren Sorgen,
        was hilft uns unser Weh und Ach?
        Was hilft es, dass wir alle Morgen
        beseufzen unser Ungemach?
        Wir machen unser Kreuz und Leid
        nur größer durch die Traurigkeit.

        3. Man halte nur ein wenig stille
        und sei doch in sich selbst vergnügt,
        wie unser's Gottes Gnadenwille,
        wie sein Allwissenheit es fügt;
        Gott, der uns sich hat auserwählt,
        der weiß auch sehr wohl, was uns fehlt.

        4. Er kennt die rechten Freudenstunden,
        er weiß wohl, wann es nützlich sei;
        wenn er uns nur hat treu erfunden
        und merket keine Heuchelei,
        so kommt Gott, eh wir's uns versehn,
        und lässet uns viel Guts geschehn.

        5. Denk nicht in deiner Drangsalshitze,
        dass du von Gott verlassen seist
        und dass ihm der im Schoße sitze,
        der sich mit stetem Glücke speist.
        Die Folgezeit verändert viel
        und setzet jeglichem sein Ziel.

        6. Es sind ja Gott sehr leichte Sachen
        und ist dem Höchsten alles gleich:
        Den Reichen klein und arm zu machen,
        den Armen aber groß und reich.
        Gott ist der rechte Wundermann,
        der bald erhöhn, bald stürzen kann.

        7. Sing, bet und geh auf Gottes Wegen,
        verricht das Deine nur getreu
        und trau des Himmels reichem Segen,
        so wird er bei dir werden neu;
        denn welcher seine Zuversicht
        auf Gott setzt, den verlässt er nicht.
        """))

    # for obj in Song.objects.all():
    #     for i in range(obj.id % 3):
    #         yield Tag(owner=obj, topic=TOPICS.pop())

    # ar = rt.login(dd.plugins.users.get_demo_user().username)
    # create_special_pages(ar)

    for pg in Page.objects.filter(special_page=SpecialPages.home):
        pg.body += "\n[show songs.LatestSongs]\n"
        yield pg

    sb1 = Page(title="Songbook", language="en",
               publishing_state="published",
               body="Here is our collection of great songs.")
    yield sb1
    sb2 = Page(title="New songbook", language="en",
               publishing_state="draft",
               body="Here is the draft of our new songbook.")
    yield sb2
    for sng in Song.objects.all():
        yield PageItem(ticket=sng, page=sb2)
        if sng.id % 2:
            yield PageItem(ticket=sng, page=sb1)
