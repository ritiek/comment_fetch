from bs4 import BeautifulSoup, element
import requests


class Comment:
    def __init__(self, author, url, timestamp, text, reactions):
        self.author = author
        self.url = url
        self.timestamp = timestamp
        self.text = text
        self.reactions = reactions


class Issue:
    def __init__(self, url):
        self.url = url
        self.page_content = requests.get(url).text

    def fetch_comments(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")

        comments = []

        comment_soup = soup.find("a", {"class":"author link-gray-dark css-truncate-target width-fit"})
        while comment_soup:
            author = comment_soup.get_text()
            text = comment_soup.find_next("div", {"class":"edit-comment-hide js-edit-comment-hide"}).get_text().strip('\n')
            try:
                timestamp = comment_soup.find_next("a", {"class":"link-gray js-timestamp"})["href"]
                url = self.url + timestamp
            except TypeError:
                timestamp = None
                url = None

            next_comment_soup = comment_soup.find_next("a", {"class":"author link-gray-dark css-truncate-target width-fit"})
            if next_comment_soup is None:
                has_reactions = bool(comment_soup.find_next("div", {"class": "comment-reactions-options"}))
            else:
                has_reactions = comment_soup.find_next("div", {"class": "comment-reactions-options"}) == next_comment_soup.find_previous("div", {"class": "comment-reactions-options"}) != None

            reactions = []
            if has_reactions:
                reactions_soup = comment_soup.find_next("div", {"class": "comment-reactions-options"})
                for reaction_soup in reactions_soup.find_all("button"):
                    reaction = {
                        "alias": reaction_soup.find("g-emoji")["alias"],
                        "quantity": int("".join([t for t in reaction_soup.contents if type(t)==element.NavigableString]))
                    }
                    reactions.append(reaction)

            comment_soup = next_comment_soup
            comment = Comment(author, url, timestamp, text, reactions)
            comments.append(comment)

        return comments


class Pages:
    def __init__(self, username):
        self.username = username

    def fetch_issues(self, page_number):
        comment_search_url = "https://github.com/search?o=desc&p=" + str(page_number) + "&q=commenter%3A" + self.username + "&s=created&type=Issues"
        response = requests.get(comment_search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all('h3', {'text-normal flex-auto pb-1'})

        issues = []
        for tag in tags:
            a = tag.find('a')
            issue_url = "https://github.com" + a['href']
            issue = Issue(issue_url)
            issues.append(issue)

        return issues


class User:
    def __init__(self, username):
        self.username = username

    def total_pages(self):
        comment_search_url = "https://github.com/search?q=commenter%3A" + self.username + "&type=Issues"
        response = requests.get(comment_search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_navigation_bar = soup.find("div", {"class": "d-flex d-md-inline-block pagination"})
        last_page = page_navigation_bar.find_all("a")[-2].get_text()
        return int(last_page)

    def fetch_page(self, page_number):
        page_fetcher = Pages(self.username)
        issues = page_fetcher.fetch_issues(page_number)
        return issues


if __name__ == "__main__":
    ritiek = User("ritiek")
    pages = ritiek.total_pages()
    for page_number in range(pages):
        issues = ritiek.fetch_page(page_number)
        for issue in issues:
            print(issue.url)
            comments = issue.fetch_comments()
            for comment in comments:
                if comment.author == "ritiek":
                    print(comment.url)
                    for reaction in comment.reactions:
                        print(list(reaction.values()))
                    print()
