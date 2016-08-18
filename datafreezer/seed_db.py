import requests
import random
from csv import reader
from bs4 import BeautifulSoup

from models import *
from views import parse_csv_headers, HUBS_LIST, STAFF_LIST


FILLER = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed pretium nulla ipsum, id suscipit sem sollicitudin sit amet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Praesent et tortor nec sem ullamcorper maximus nec id lectus. Maecenas volutpat dolor ut velit facilisis, sit amet pretium erat convallis. Proin vel purus pulvinar, bibendum dolor cursus, congue erat. Sed interdum, neque eget molestie venenatis, nulla ex aliquet odio, sit amet rutrum metus urna at velit. Cras consectetur augue eu tincidunt blandit.
Praesent congue, elit vel sollicitudin tincidunt, lorem lectus rhoncus justo, et porttitor nisi sapien eu arcu. Aliquam molestie sed leo quis aliquam. Praesent elementum eros fermentum libero pellentesque pharetra. Nam tristique neque ut est bibendum cursus. Fusce ac purus quis purus dictum efficitur et eu nisi. Etiam a ligula posuere nibh convallis imperdiet. Integer nec vulputate libero. Sed consectetur semper tempor. Vivamus consectetur libero ex, sed bibendum nulla maximus et. Vestibulum egestas mauris vitae magna luctus, eu feugiat nulla vestibulum. Cras ac porta leo, a imperdiet neque. Vestibulum vitae nulla vel ex tempor cursus. Maecenas scelerisque eu quam ut suscipit. Vestibulum eu gravida justo. Proin vitae tortor scelerisque, iaculis lectus eu, interdum mi.
'''.split()

DMN_URL = 'http://www.dallasnews.com'

def grab_dmn_article_urls(url):
    resp = requests.get(url)
    page = resp.content
    soup = BeautifulSoup(page, 'html.parser')
    return [link['href'] for link in soup.find_all('a') if link['href'][len(link)-4:] == 'ece']


def scrape_article_title(url):
    article_req = requests.get(url)
    if article_req.status_code == 200:
        # We good. Get the HTML.
        page = article_req.content
        soup = BeautifulSoup(page, 'html.parser')
        #Looking for <meta ... property="og:title">
        meta_title_tag = soup.find('meta', attrs={'property': 'og:title'})
        try:
            # print "Trying og:title..."
            # print meta_title_tag
            title = meta_title_tag['content']
        # TypeError implies meta_title_tag is None
        # KeyError implies that meta_title_tag does not have a content property.
        except (TypeError, KeyError):
            title_tag = soup.find('title')
            try:
                # print "Falling back to title..."
                # print title_tag
                title = title_tag.text
            except (TypeError, KeyError):
                description_tag = soup.find('meta', attrs={'property': 'og:description'})
                try:
                    # print "Falling back to description..."
                    # print description_tag
                    title = description_tag['content']
                # Fall back value. Display is handled in models.
                except (TypeError, KeyError):
                    title = None
        return title


def prepare_articles():
    url_list = grab_dmn_article_urls(DMN_URL)

    articles = []
    for url in url_list:
        url = url.strip()
        if len(url) > 0:
            article, created = Article.objects.get_or_create(url=url)
            if created:
                article.title = scrape_article_title(url)
                article.save()
        articles.append(article)

    return articles


def create_dataset_title():
    title = ""
    numWords = random.randint(4, 12)
    exclude = set(string.punctuation)

    for counter in range(numWords):
        randIndex = random.randint(0, len(FILLER)-1)
        word = FILLER[randIndex] + " "
        word = ''.join(ch for ch in word if ch not in exclude)
        title += word

    return title.title().strip()



def create_dataset_description(maxLength):
    desc = ""
    numWords = random.randint(15, maxLength)

    for counter in range(numWords):
        randIndex = random.randint(0, len(FILLER)-1)
        word = FILLER[randIndex] + " "
        desc += word

    return desc.strip()


def choose_dataset_tags():
    # available_tags = Tag.objects.all()

    exclude = set(string.punctuation)

    for counter in range(25):
        tagWord = FILLER[random.randint(0, len(FILLER)-1)].lower()
        tagWord = ''.join(ch for ch in tagWord if ch not in exclude)
        tag = Tag.objects.get_or_create(
            slug=slugify(tagWord),
            defaults={
                'word': tagWord
            }
        )
    # numTags = random.randint(1, available_tags.count())
    #
    # tags = []
    #
    # for counter in range(numTags):
    #     randIndex = random.randint(0, available_tags.count() - 1)
    #     if available_tags[randIndex].word not in tags:
    #         tags.append(available_tags[randIndex].word)

    return Tag.objects.all()


def choose_dataset_articles(articles):
    numArticles = random.randint(1, len(articles) / 4)

    chosen_articles = []

    for counter in range(numArticles):
        randIndex = random.randint(0, len(articles) - 1)
        chosen_articles.append(articles[randIndex])

    return chosen_articles


def prepare_data_dict(dataset_id):
    data_dict = DataDictionary(author='tydavis@dallasnews.com')
    data_dict.save()

    data = Dataset.objects.get(pk=dataset_id)
    with open(data.dataset_file.path, 'r') as datasetFile:
        read = reader(datasetFile, delimiter=',', quotechar='"')
        headers = next(read)

    fields = []

    for header in headers:
        field = DataDictionaryField(
            heading=header,
            description=create_dataset_description(25),
            dataType="TEXT"
        )
        field.parent_dict = data_dict
        field.save()

    return data_dict


def create_datasets(num_datasets):

    for counter in range(num_datasets):
        created_dataset = Dataset(
            title=create_dataset_title(),
            description=create_dataset_description(100)
        )


        created_dataset.dataset_file = './datafreezer/uploads/crimes_by_tract.csv'
        created_dataset.has_headers = True

        # uploaders = ['tydavis@dallasnews.com', 'ajvestal@dallasnews.com', 'jmcclure@dallasnews.com']

        created_dataset.uploaded_by = STAFF_LIST[random.randint(0, len(STAFF_LIST)-1)]['email']

        hubIndex = random.randint(0, len(HUBS_LIST)-1)
        created_dataset.hub_slug = HUBS_LIST[hubIndex]['slug']

        created_dataset.vertical_slug = HUBS_LIST[hubIndex]['vertical']['slug']

        created_dataset.save()
        d_id = created_dataset.id
        print d_id

        datadict = prepare_data_dict(d_id)

        created_dataset.data_dictionary = datadict

        tags = choose_dataset_tags()

        numTags = random.randint(1, (num_datasets/10))

        for counter in range(numTags):
            tagIndex = random.randint(0, len(tags)-1)
            created_dataset.tags.add(tags[tagIndex])

        # for tag in tags:
    	# 	tagToAdd, created = Tag.objects.get_or_create(slug=slugify(tag), defaults={'word': tag})
    	# 	created_dataset.tags.add(tagToAdd)

        all_articles = prepare_articles()
        dataset_articles = choose_dataset_articles(all_articles)

        for article in dataset_articles:
            created_dataset.appears_in.add(article)

        created_dataset.save()
