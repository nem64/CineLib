import requests
import base64

class Cinemana:
    """An interface for querying the Cinemana API and extracting the download links.
    """
    def __init__(self, title):
        self.seasons = 0
        self.episodes = 0
        self.title = title
        self.id = self.search()[0]['id']
        self.links = self.getLinks()

    def _b64e(self, s):
        return base64.b64encode(s.encode()).decode().replace('=', '') # Cinemana wants a base64 string which is not padded, so we remove the padding

    
    def getEpisode(self, season, episode):
        """Gets a direct link for a media
        If the media is a movie and not a series, the 2 arguments should both be 0 else it will not return anything.

        Outputs a string
        """
        for ep in self.links:
            if(ep['season'] == season and ep['episode'] == episode):
                return ep['url']

    def search(self):
        """Queries the Cinemana API about the title and returns the results
        Use this if you want to get multiple results, this is not needed for the basic functionality of fetching a media and manipulating it

        Outputs a list with dictionaries {id: X, title: Y}
        """
        searchReq = requests.get(
            'https://cinemana.shabakaty.com/api/android/video/V/2/itemsPerPage/1/video_title_search/%s/itemsPerPage/25/pageNumber/0/level/0' % self._b64e(self.title))
        searchResp = searchReq.json()

        cleaned = []

        for elem in searchResp:
            cleaned.append({'id': elem['nb'],
                            'title': elem['en_title']})
        return cleaned


    def getLinks(self):
        """Gets all the links of all medias associated with the resulting ID from the title, then remove unimportant data.
        This also counts the seasons and the episodes.

        Outputs a sorted list with a dictionary for each media, Including the season and episode associated with the link if available
        """
        metaReq = requests.get(
            'https://cinemana.shabakaty.com/api/android/videoSeason/id/%s' % self.id)
        metaResp = metaReq.json()

        cleaned = []

        if(metaReq.text == '[]'):  # This is a movie, don't waste time and loop (Also this endpoint returns [] when it's NOT a series)
            urlReq = requests.get(
                'https://cinemana.shabakaty.com/api/android/transcoddedFiles/id/%s' % self.id)
            urlResp = urlReq.json()

            cleaned.append({'season': 0, 'episode': 0,
                        'url': urlResp[-1]['videoUrl']})
            return cleaned

        for elem in metaResp:  # This is a series
            season = int(elem['season']) #Preload the variables
            episode = int(elem['episodeNummer']) # so we don't have to pointlessly redo it 
            urlReq = requests.get(
                'https://cinemana.shabakaty.com/api/android/transcoddedFiles/id/%s' % elem['nb'])
            urlResp = urlReq.json()
            cleaned.append({'season': season,
                            'episode': episode, 'url': urlResp[-1]['videoUrl']})            
            
            if(self.seasons < season): # While we're in the loop, count the seasons and episodes available. I don't trust Cinemana's supplied info in that regard.
                self.seasons = season
            
            self.episodes += 1

        return sorted(cleaned, key=lambda cleaned: cleaned['season'])