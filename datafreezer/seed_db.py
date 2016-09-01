# Imports from python.  # NOQA
from csv import reader
import random
import string


# Imports from django.
from django.utils.text import slugify


# Imports from datafreezer.
from datafreezer.apps import HUBS_LIST, STAFF_LIST  # NOQA
from datafreezer.models import (
    Article,  # NOQA
    DataDictionary,
    DataDictionaryField,
    Dataset,
    Tag,
)
# from datafreezer.views import parse_csv_headers


# Imports from other dependencies.
from bs4 import BeautifulSoup
import progressbar
import requests


FILLER = ' '.join([
    'Paul Steiger fourth estate horse-race coverage TBD but what\'s the',
    'business model Groupon content farm hyperhyperhyperlocal, Fuego trolls',
    'crowdfunding link economy engagement process vs. product, content is',
    'king advertising perfect for starting a campfire natural-born blogger',
    'information overload natural-born blogger. hyperlocal Robin Sloan',
    'Colbert bump bot Fuego West Seattle Blog in the slot curation TweetDeck',
    'Journal Register, privacy the medium is the message Jay Rosen media diet',
    'gutter pay curtain hackgate collaboration, a giant stack of newspapers',
    'that you\'ll never read +1 Gawker innovation Reuters The Printing Press',
    'as an Agent of Change social media TweetDeck. libel lawyer MinnPost the',
    'medium is the message Frontline go viral people formerly known as the',
    'audience dead trees NPR stupid commenters try PR curmudgeon Flipboard',
    'tablets, CNN leaves it there abundance Does my "yes, but" look big in',
    'this corner office? link economy recontextualize tablets digital',
    'circulation strategy process vs. product pay curtain WordPress Flipboard',
    'RSS Ushahidi, Neil Postman natural-born blogger social media',
    'optimization backpack journalist put the paper to bed Jeff Jarvis nut',
    'graf Snarkmarket I saw it on Mediagazer future of context Patch. A.J.',
    'Liebling social media optimization Romenesko analog thinking shoot a',
    'photo RSS if the news is that important, it\'ll find me newsroom cafe',
    'analog thinking hackgate Colbert bump, abundance view from nowhere',
    'mathewi process vs. product David Cohn do what you do best and link to',
    'the rest future of narrative hot news doctrine Journal Register digital',
    'first, paidContent Journal Register gamification horse-race coverage',
    'Lucius Nieman content farm innovation Walter Lippmann future. Like',
    'button we need a Nate Silver iPhone app bot the notional night cops',
    'reporter in Des Moines newsonomics got drudged, analog thinking Zite',
    'cancel my subscription cops beat Quora CNN leaves it there Free Darko,',
    'cognitive surplus mathewi the medium is the massage collaboration',
    'hyperhyperhyperlocal. attracting young readers perfect for starting a',
    'campfire the medium is the massage Arianna open newsroom TechCrunch the',
    'notional night cops reporter in Des Moines NYT R&D innovation',
    'paidContent, circulation Fuego stream gutter the notional night cops',
    'reporter in Des Moines This Week in Review dingbat backpack journalist,',
    'Julian Assange hot news doctrine explainer Project Thunderdome media',
    'bias Free Darko Bill Keller church of the savvy. Walter Cronkite died',
    'for your sins Knight Foundation if the news is that important, it\'ll',
    'find me newsroom cafe abundance mthomps synergize crowdfunding tablets',
    'Jeff Jarvis, lede Jurgen Habermas curation writing metered model',
    'cognitive surplus if the news is that important, it\'ll find me the',
    'audience knows more than I do, stream tablets startups NPR curation',
    'commons-based peer production hot news doctrine AP. newsonomics process',
    'vs. product the medium is the massage Nook WikiLeaks data visualization',
    'iPhone app, Buttry view from nowhere privacy Marshall McLuhan mthomps',
    'cognitive surplus SEO, The Weekender vast wasteland linkbait Josh',
    'Marshall filters. Colbert bump +1 go viral should isn\'t a business',
    'model Frontline linkbait kitchen table of the future tags, Frontline',
    'Gutenberg parenthesis pay curtain Frontline David Cohn got drudged, Clay',
    'Shirky the medium is the massage Gawker just across the wire Gannett',
    'tags. Flipboard recontextualize explainer reporting Flipboard hashtag if',
    'the news is that important, it\'ll find me advertising put the paper to',
    'bed do what you do best and link to the rest gotta grok it before you',
    'rock it Facebook the medium is the massage inverted pyramid, algorithms',
    'cancel my subscription mthomps Groupon David Cohn Mozilla HuffPo future',
    'of narrative gamification lede perfect for starting a campfire Colbert',
    'bump. social media Dayton for under $900 a day Innovator\'s Dilemma',
    'synergize right-sizing church of the savvy cops beat process vs. product',
    'newspaper strike Romenesko, the audience knows more than I do Buttry',
    'data journalism NPR Free Darko Facebook analytics linking, monetization',
    'RSS TechCrunch backpack journalist bloggers in their mother\'s basement',
    'The Daily every dog loves food cognitive surplus. advertising RSS',
    'Alberto Ibarguen Flipboard tags cognitive surplus hyperlocal social',
    'media optimization plagiarism, Dayton for under $900 a day Voice of San',
    'Diego retweet recontextualize media diet WaPo data visualization. Dayton',
    'for under $900 a day the audience knows more than I do Buttry Fuego Nook',
    '5 praise erasers & how to avoid them Politics & Socks page Dayton for',
    'under $900 a day monetization, in the slot community right-sizing the',
    'notion of the public dead trees TechCrunch tags Arab spring, Kindle',
    'Single Dayton for under $900 a day data visualization newspaper kitchen',
    'table of the future scoop masthead. I love the Weather & Opera section',
    'Project Thunderdome Gutenberg experiment stupid commenters content is',
    'king AP nonprofit, curmudgeon should isn\'t a business model HuffPo',
    'Reuters twitterati Patch MinnPost, Jay Rosen dead trees the medium is',
    'the massage Tim Carmody nonprofit community. Walter Lippmann audience',
    'atomization overcome paidContent TechCrunch eHow Nick Denton 5%',
    'corruption a giant stack of newspapers that you\'ll never read Does my',
    '"yes, but" look big in this corner office? Tumblr recontextualize,',
    'Project Thunderdome Dayton for under $900 a day Colbert bump Snarkmarket',
    'David Foster Wallace Wikipedia dead trees backpack journalist analytics',
    'get me rewrite, CPM meme Jay Rosen synergize TweetDeck dying data',
    'visualization he said she said fair use. gamification Instagram 5%',
    'corruption Voice of San Diego pay curtain Mozilla Dayton for under $900',
    'a day WSJ The Printing Press as an Agent of Change aggregation',
    'algorithms, Storify blog morgue Nook API lede the medium is the massage',
    'every dog loves food audience atomization overcome. Gannett lede mthomps',
    'social media newsonomics Demand Media paidContent analog thinking Knight',
    'News Challenge abundance, 5 praise erasers & how to avoid them Patch',
    'data journalism Django put the paper to bed try PR curation The',
    'Weekender, awesome people formerly known as the audience What Would',
    'Google Do the notion of the public open newsroom tweets David Foster',
    'Wallace Rupert Murdoch. Instagram +1 production of innocence tags',
    'curmudgeon advertising writing Demand Media hyperhyperhyperlocal,',
    'linkbait mathewi Reuters semipermeable Colbert bump RT David Cohn',
    'Gannett, monetization crowdsourcing afternoon paper Robin Sloan RT',
    'Foursquare hackgate. social media Jeff Jarvis prostate Politics & Socks',
    'page RT pay curtain NYT R&D he said she said Like button circulation,',
    'serendipity Pictures of Goats section morgue the notion of the public',
    'collaboration process vs. product Fuego do what you do best and link to',
    'the rest, right-sizing future The Printing Press as an Agent of Change',
    'Quora paywall analog thinking media diet. eHow iPad app experiment',
    'crowdsourcing ProPublica Jay Rosen information wants to be free',
    'Frontline, Ushahidi link economy Sulzberger gutter libel lawyer we will',
    'make them pay Gannett attracting young readers, copyright Sulzberger',
    'eHow tweet the audience knows more than I do nonprofit. view from',
    'nowhere Gawker Free Darko collaboration Knight Foundation tablets',
    'copyboy, discuss dingbat monetization twitterati social media',
    'optimization Innovator\'s Dilemma, social media optimization anonymity',
    'Ushahidi Demand Media eHow.',
]).split()


DMN_URL = 'http://www.dallasnews.com'


def grab_dmn_article_urls(url):
    resp = requests.get(url)
    page = resp.content
    soup = BeautifulSoup(page, 'html.parser')
    return [
        link['href']
        for link in soup.find_all('a')
        if link['href'][len(link)-4:] == 'ece'
    ]


def scrape_article_title(url):
    article_req = requests.get(url)
    if article_req.status_code == 200:
        # We good. Get the HTML.
        page = article_req.content
        soup = BeautifulSoup(page, 'html.parser')

        # Looking for <meta ... property="og:title">
        meta_title_tag = soup.find('meta', attrs={'property': 'og:title'})
        try:
            # print "Trying og:title..."
            # print meta_title_tag
            title = meta_title_tag['content']

        # TypeError implies meta_title_tag is None
        # KeyError implies that meta_title_tag has no content property.
        except (TypeError, KeyError):
            title_tag = soup.find('title')
            try:
                # print "Falling back to title..."
                # print title_tag
                title = title_tag.text
            except (TypeError, KeyError):
                description_tag = soup.find(
                    'meta',
                    attrs={'property': 'og:description'}
                )
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


def choose_source():
    exclude = set(string.punctuation)

    source = ""

    while source == "":
        source = FILLER[random.randint(0, len(FILLER)-1)].strip().title()
        source = ''.join(ch for ch in source if ch not in exclude)

    return source


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
        if tagWord is not '':
            # tag = Tag.objects.get_or_create(
            Tag.objects.get_or_create(
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

    # fields = []

    col = 0
    for header in headers:
        col += 1
        field = DataDictionaryField(
            heading=header,
            description=create_dataset_description(25),
            dataType="TEXT",
            columnIndex=col
        )
        field.parent_dict = data_dict
        field.save()

    return data_dict


def create_datasets(num_datasets):

    tags = choose_dataset_tags()

    bar = progressbar.ProgressBar()

    for counter in bar(range(num_datasets)):
        created_dataset = Dataset(
            title=create_dataset_title(),
            description=create_dataset_description(100)
        )

        created_dataset.dataset_file = '/'.join([
            '2016/08/18',
            'neighborhood_crime_zscores.csv'
        ])
        created_dataset.has_headers = True

        # uploaders = [
        #     'tydavis@dallasnews.com',
        #     'ajvestal@dallasnews.com',
        #     'jmcclure@dallasnews.com',
        # ]

        created_dataset.uploaded_by = STAFF_LIST[
            random.randint(0, len(STAFF_LIST)-1)
        ]['email']

        hubIndex = random.randint(0, len(HUBS_LIST)-1)
        created_dataset.hub_slug = HUBS_LIST[hubIndex]['slug']

        created_dataset.vertical_slug = HUBS_LIST[hubIndex]['vertical']['slug']

        # source = FILLER[random.randint(0, len(FILLER)-1)]
        source = choose_source()
        created_dataset.source = source
        created_dataset.source_slug = slugify(source)

        created_dataset.save()
        d_id = created_dataset.id
        # print d_id

        datadict = prepare_data_dict(d_id)

        created_dataset.data_dictionary = datadict

        numTags = random.randint(1, (num_datasets/10))

        for counter in range(numTags):
            tagIndex = random.randint(0, len(tags)-1)
            created_dataset.tags.add(tags[tagIndex])

        # for tag in tags:
        #     tagToAdd, created = Tag.objects.get_or_create(
        #         slug=slugify(tag),
        #         defaults={'word': tag}
        #     )
        #     created_dataset.tags.add(tagToAdd)

        all_articles = prepare_articles()
        dataset_articles = choose_dataset_articles(all_articles)

        for article in dataset_articles:
            created_dataset.appears_in.add(article)

        created_dataset.save()
