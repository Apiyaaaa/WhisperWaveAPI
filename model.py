class News:
    # if none assign default value
    def __init__(self, title, link, content=None, source=None, date=None, author=None, ai_summary=None, embedding=None) -> None:
        self.title = title
        self.link = link
        self.content = content
        self.source = source
        self.date = date
        self.author = author
        self.ai_summary = ai_summary
        self.embedding = embedding

    def get(self):
        return {
            'title': self.title,
            'link': self.link,
            'content': self.content,
            'source': self.source,
            'date': self.date,
            'author': self.author,
            'ai_summary': self.ai_summary,
            'embedding': self.embedding
        }