import shutil
import mangadex
import os

config_file = "followed.txt"
download_dir = "akari_downloads"
mobi_dir = "mobi"
command_str = "kcc-c2e -m -u -o ../"


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
    try:
        manga = mangadex.Manga(manga_id).populate()
    except:
        print("[ERROR] Invalid manga id")
        return ch_id_from
    title = getattr(manga, "title")

    if download_dir not in os.listdir(os.getcwd()):
        os.mkdir(download_dir)
    os.chdir(download_dir)

    if ch_id_from == "0":
        chapters = get_chapter_list(manga)
    elif ch_id_from not in list(map(lambda ch: ch.cached_chapter, get_chapter_list(manga))):
        print("[ERROR] Invalid chapter id")
        os.chdir("..")
        return ch_id_from
    else:
        chapters = get_chapters_from(get_chapter_list(manga), ch_id_from)

    print("[CHECK] " + str(len(chapters)) + " new" + " -> " + title)

    if chapters == []:
        os.chdir("..")
        return ch_id_from
    last_chapter_id = chapters[0].cached_chapter

    if title not in os.listdir(os.getcwd()):
        os.mkdir(title)
    os.chdir(title)

    print("[MANGA] " + title + " " + list(map(lambda ch: ch.cached_chapter, chapters)).__str__())
    for chapter in chapters:
        download_chapter(chapter)
    os.chdir("../..")

    return last_chapter_id


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
    print("[STATUS] Done downloading")


def update_file(filename, mangas):
    print("[STATUS] Updating config file")
    file = open(filename, "w+")
    file.seek(0)
    file.truncate()
    for id, ch in mangas:
        file.write(id + "," + str(ch) + "\n")
    file.close()
    print("[STATUS] Done updating config file")


def make_mobis():
    print("[STATUS] Creating mobi files")
    if mobi_dir not in os.listdir(os.getcwd()):
        os.mkdir(mobi_dir)
    os.chdir(download_dir)
    for filename in os.listdir():
        command = command_str + mobi_dir + " \"" + os.getcwd() + "/" + filename + "/" + "\" "
        try:
            os.system(command)
        except:
            print("[ERROR] Couldn't create mobi")
    os.chdir("..")
    print("[STATUS] Done creating mobi files")


mangas = load_mangas(config_file)
download_followed(mangas)
update_file(config_file, mangas)

try:
    make_mobis()
except:
    print("[ERROR] " + "Could not create mobi")

try:
    shutil.rmtree(download_dir)
except:
    pass
