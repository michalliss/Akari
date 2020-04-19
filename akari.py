import shutil
import mangadex
import os

download_dir = "akari_downloads"
mobi_dir = "mobi"


def get_chapter_list(manga):
    chapters = manga.populate().get_chapters()
    chapters = list(filter(lambda ch: ch.cached_lang_code == 'gb', chapters))

    return chapters


def get_chapter(chapters, ch_id):
    chapter = list(filter(lambda ch: ch.cached_chapter == ch_id, chapters))[0].populate()
    return chapter


def get_chapters_from(chapters, ch_id_from):
    ch_from = get_chapter(chapters, str(ch_id_from))
    chapters = chapters[:chapters.index(ch_from)]
    return chapters


def download_chapter(chapter):
    if chapter.cached_chapter not in os.listdir(os.getcwd()):
        os.mkdir(chapter.cached_chapter)
    os.chdir(chapter.cached_chapter)
    print("[DOWNLOAD] Chapter " + chapter.cached_chapter)
    for page in chapter.get_pages():
        page.download()
    os.chdir("..")


def download_manga(manga_id, ch_id_from):
    manga = mangadex.Manga(manga_id).populate()
    title = getattr(manga, "title")

    if download_dir not in os.listdir(os.getcwd()):
        os.mkdir(download_dir)
    os.chdir(download_dir)

    if ch_id_from == 0:
        chapters = get_chapter_list(manga)
    else:
        chapters = get_chapters_from(get_chapter_list(manga), ch_id_from)

    if chapters == []:
        os.chdir("..")
        return ch_id_from

    if title not in os.listdir(os.getcwd()):
        os.mkdir(title)
    os.chdir(title)

    last_chapter = chapters[0].cached_chapter
    print("[MANGA] " + title)
    for chapter in chapters:
        download_chapter(chapter)
    os.chdir("../..")

    return last_chapter


def load_mangas(filename):
    mangas = []
    file = open(filename)
    for line in file:
        splited = line.strip().split(",")
        id = splited[0]
        chapter = splited[1]
        mangas.append((id, chapter))
    file.close()
    return mangas


def download_followed(mangas):
    for i, (manga_id, ch_from) in enumerate(mangas):
        mangas[i] = manga_id, download_manga(manga_id, ch_from)


def update_file(filename, mangas):
    file = open(filename, "w+")
    file.seek(0)
    file.truncate()
    for id, ch in mangas:
        file.write(id + "," + str(ch) + "\n")
    file.close()


def make_mobis():
    if mobi_dir not in os.listdir(os.getcwd()):
        os.mkdir(mobi_dir)
    os.chdir(download_dir)
    for filename in os.listdir():
        command = "kcc-c2e -m -u -o ../" + mobi_dir + " \"" + os.getcwd() + "/" + filename + "/" + "\" "
        os.system(command)
    os.chdir("..")


mangas = load_mangas("followed.txt")
download_followed(mangas)
update_file("followed.txt", mangas)

make_mobis()

try:
    shutil.rmtree(download_dir)
except:
    pass
