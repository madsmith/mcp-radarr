import pytest
from mcp_radarr.types import MovieDetailsFull

@pytest.fixture
def sample_movie_data():
    """Sample movie data from Radarr API"""
    return  {
        "title": "Inception",
        "originalTitle": "Inception",
        "originalLanguage": {
            "id": 1,
            "name": "English"
        },
        "alternateTitles": [
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "El Origen",
            "id": 6919
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\uc778\uc149\uc158",
            "id": 6920
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "A Origem",
            "id": 6921
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Ba\u015flang\u0131\u00e7",
            "id": 6922
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u6f5b\u884c\u51f6\u9593",
            "id": 6923
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u76d7\u68a6\u7a7a\u95f4",
            "id": 6924
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Eredet",
            "id": 6925
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Pirms\u0101kums",
            "id": 6926
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0e08\u0e34\u0e15\u0e1e\u0e34\u0e06\u0e32\u0e15\u0e42\u0e25\u0e01",
            "id": 6927
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u5168\u9762\u555f\u52d5",
            "id": 6928
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u5960\u57fa",
            "id": 6929
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u5fc3\u7075\u72af\u6848",
            "id": 6930
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u8bb0\u5fc6\u8ff7\u9635",
            "id": 6931
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u8bb0\u5fc6\u9b54\u65b9",
            "id": 6932
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "K\u1ebb Tr\u1ed9m Gi\u1ea5c M\u01a1",
            "id": 6934
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u062a\u0644\u0642\u06cc\u0646",
            "id": 6935
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u30a4\u30f3\u30bb\u30d7\u30b7\u30e7\u30f3",
            "id": 18651
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Orixe",
            "id": 18652
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Dechreuad y Creu",
            "id": 18653
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Algus",
            "id": 18654
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Po\u010detak",
            "id": 18655
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Prad\u017eia",
            "id": 18656
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Muqaddima",
            "id": 18657
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Incepcja",
            "id": 18658
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u00cenceputul",
            "id": 18659
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Po\u010diatok",
            "id": 18660
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Izvor",
            "id": 18661
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Huglj\u00f3mun",
            "id": 18662
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "Po\u010d\u00e1tek",
            "id": 18663
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u041f\u0430\u0447\u0430\u0442\u0430\u043a",
            "id": 18664
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0413\u0435\u043d\u0435\u0437\u0438\u0441",
            "id": 18665
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0411\u0430\u0448\u0442\u0430\u043b\u044b\u0448",
            "id": 18666
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u041f\u043e\u0447\u0435\u0442\u043e\u043a",
            "id": 18667
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0423\u0448\u0435\u0434\u043e\u043c\u0430",
            "id": 18668
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u041e\u0440\u0448\u0438\u043b",
            "id": 18669
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u041d\u0430\u0447\u0430\u043b\u043e",
            "id": 18670
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u041f\u043e\u0447\u0430\u0442\u043e\u043a",
            "id": 18671
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u054d\u056f\u056b\u0566\u0562",
            "id": 18672
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u05d4\u05ea\u05d7\u05dc\u05d4",
            "id": 18673
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0627\u0646\u0633\u067e\u0634\u0646",
            "id": 18674
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0627\u0633\u062a\u0647\u0644\u0627\u0644",
            "id": 18675
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0628\u0627\u0634\u0644\u0627\u0646\u063a\u06cc\u062c",
            "id": 18676
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0627\u06cc\u0646\u0633\u067e\u0634\u0646",
            "id": 18677
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0627\u0632\u062f\u0631\u0627\u0639",
            "id": 18678
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u062f\u06d5\u0633\u062a\u067e\u06ce\u06a9",
            "id": 18679
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0907\u0928\u094d\u0938\u0947\u092a\u094d\u0938\u0928",
            "id": 18680
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0907\u0928\u094d\u0938\u0947\u092a\u094d\u0936\u0928",
            "id": 18681
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0987\u09a8\u09b8\u09c7\u09aa\u09b6\u09a8",
            "id": 18682
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0a07\u0a28\u0a38\u0a48\u0a2a\u0a38\u0a3c\u0a28",
            "id": 18683
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0b87\u0ba9\u0bcd\u0b9a\u0bc6\u0baa\u0bcd\u0b9a\u0ba9\u0bcd",
            "id": 18684
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0c87\u0ca8\u0ccd\u0cb8\u0cc6\u0caa\u0ccd\u0cb7\u0ca8\u0ccd",
            "id": 18685
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u0d07\u0d7b\u0d38\u0d46\u0d2a\u0d4d\u0d37\u0d7b",
            "id": 18686
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u10d3\u10d0\u10ed\u10e7\u10d0\u10e4\u10e3\u10e0\u10d8",
            "id": 18687
            },
            {
            "sourceType": "tmdb",
            "movieMetadataId": 796,
            "title": "\u10d3\u10d0\u10e1\u10d0\u10ec\u10e7\u10d8\u10e1\u10d8",
            "id": 18688
            }
        ],
        "secondaryYearSourceId": 0,
        "sortTitle": "inception",
        "status": "released",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
        "inCinemas": "2010-07-15T00:00:00Z",
        "physicalRelease": "2010-12-03T00:00:00Z",
        "digitalRelease": "2013-03-04T00:00:00Z",
        "images": [
            {
            "coverType": "poster",
            "url": "/MediaCover/718/poster.jpg?lastWrite=638827986535720093",
            "remoteUrl": "https://image.tmdb.org/t/p/original/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
            },
            {
            "coverType": "fanart",
            "url": "/MediaCover/718/fanart.jpg?lastWrite=638841854644753241",
            "remoteUrl": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg"
            }
        ],
        "website": "https://www.warnerbros.com/movies/inception",
        "remotePoster": "https://image.tmdb.org/t/p/original/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "year": 2010,
        "youTubeTrailerId": "cdx31ak4KbQ",
        "studio": "Legendary Pictures",
        "path": "/remote/cifs/tank/videos/movies/HD/Inception (2010)",
        "qualityProfileId": 1,
        "movieFileId": 719,
        "monitored": True,
        "minimumAvailability": "announced",
        "isAvailable": True,
        "folderName": "/remote/cifs/tank/videos/movies/HD/Inception (2010)",
        "runtime": 148,
        "cleanTitle": "inception",
        "imdbId": "tt1375666",
        "tmdbId": 27205,
        "titleSlug": "27205",
        "folder": "Inception (2010)",
        "certification": "PG-13",
        "genres": [
            "Action",
            "Science Fiction",
            "Adventure"
        ],
        "tags": [],
        "added": "2024-07-31T00:20:57Z",
        "ratings": {
            "imdb": {
            "votes": 2696583,
            "value": 8.8,
            "type": "user"
            },
            "tmdb": {
            "votes": 37584,
            "value": 8.369,
            "type": "user"
            },
            "metacritic": {
            "votes": 0,
            "value": 74,
            "type": "user"
            },
            "rottenTomatoes": {
            "votes": 0,
            "value": 87,
            "type": "user"
            }
        },
        "movieFile": {
            "movieId": 718,
            "relativePath": "Inception (2010).mkv",
            "path": "/remote/cifs/tank/videos/movies/HD/Inception (2010)/Inception (2010).mkv",
            "size": 3842002558,
            "dateAdded": "2024-07-31T00:24:07Z",
            "edition": "",
            "languages": [
            {
                "id": 1,
                "name": "English"
            }
            ],
            "quality": {
            "quality": {
                "id": 3,
                "name": "WEBDL-1080p",
                "source": "webdl",
                "resolution": 1080,
                "modifier": "none"
            },
            "revision": {
                "version": 1,
                "real": 0,
                "isRepack": False
            }
            },
            "customFormatScore": 0,
            "indexerFlags": 0,
            "mediaInfo": {
            "audioBitrate": 0,
            "audioChannels": 2,
            "audioCodec": "AAC",
            "audioLanguages": "eng/eng",
            "audioStreamCount": 2,
            "videoBitDepth": 8,
            "videoBitrate": 0,
            "videoCodec": "x264",
            "videoFps": 23.976,
            "videoDynamicRange": "",
            "videoDynamicRangeType": "",
            "resolution": "1920x800",
            "runTime": "2:28:08",
            "scanType": "Progressive",
            "subtitles": "eng"
            },
            "qualityCutoffNotMet": False,
            "id": 719
        },
        "popularity": 28.5517,
        "id": 718
    }

def test_movie_detailed_validation(sample_movie_data):
    """Test that the MovieDetailed model can parse the sample data"""
    try:
        # Try to parse the data into a MovieDetailed model
        movie = MovieDetailsFull.model_validate(sample_movie_data)
        print(f"\nValidation successful! Movie title: {movie.title} ({movie.year})")
        
        # Verify some nested fields were parsed correctly
        if movie.movieFile and movie.movieFile.mediaInfo:
            print(f"Resolution: {movie.movieFile.mediaInfo.resolution}")
        
        if movie.ratings and "imdb" in movie.ratings:
            print(f"IMDB Rating: {movie.ratings['imdb'].value} from {movie.ratings['imdb'].votes} votes")
        
        assert movie.id == 718
        assert movie.title == "Inception"
        assert movie.year == 2010
        assert movie.tmdbId == 27205

    except Exception as e:
        assert False, f"Validation failed: {e}"

if __name__ == "__main__":
    # This allows running the file directly for quick testing
    data = sample_movie_data()
    test_movie_detailed_validation(data)
