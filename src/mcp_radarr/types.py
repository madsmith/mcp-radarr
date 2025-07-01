from typing import Optional, List, Dict, Any, Union, ClassVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class RadarrError(RuntimeError):
    def __init__(self, errors: dict, status: int):
        super().__init__(f"Radarr API error {status}: {errors}")
        self.errors = errors
        self.status = status

class MovieFileMediaInfoFull(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    audioChannels: Optional[float] = None
    audioCodec: Optional[str] = None
    audioLanguages: Optional[str] = None
    audioStreamCount: Optional[int] = None
    videoBitDepth: Optional[int] = None
    videoBitrate: Optional[int] = None
    videoCodec: Optional[str] = None
    videoFps: Optional[float] = None
    videoDynamicRange: Optional[str] = None
    videoDynamicRangeType: Optional[str] = None
    resolution: Optional[str] = None
    runTime: Optional[str] = None
    scanType: Optional[str] = None
    subtitles: Optional[str] = None
    audioBitrate: Optional[int] = None

class MovieFileMediaInfoMin(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    audioChannels: Optional[float] = None
    audioCodec: Optional[str] = None
    videoDynamicRange: Optional[str] = None
    subtitles: Optional[str] = None

    @classmethod
    def fromFull(cls, full: MovieFileMediaInfoFull) -> "MovieFileMediaInfoMin":
        return cls(
            audioChannels=full.audioChannels,
            audioCodec=full.audioCodec,
            videoDynamicRange=full.videoDynamicRange,
            subtitles=full.subtitles
        )
    
class QualityInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    name: Optional[str] = None
    source: Optional[str] = None
    resolution: Optional[int] = None
    modifier: Optional[str] = None

class QualityRevision(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    version: Optional[int] = None
    real: Optional[int] = None
    isRepack: Optional[bool] = None

class MovieFileQuality(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    quality: Optional[QualityInfo] = None
    revision: Optional[QualityRevision] = None

class Language(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    name: Optional[str] = None

class MovieFileFull(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    movieId: Optional[int] = None
    relativePath: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    dateAdded: Optional[str] = None
    edition: Optional[str] = None
    quality: Optional[MovieFileQuality] = None
    mediaInfo: Optional[MovieFileMediaInfoFull] = None
    languages: Optional[List[Language]] = None
    customFormatScore: Optional[int] = None
    indexerFlags: Optional[int] = None
    qualityCutoffNotMet: Optional[bool] = None

class MovieFileMin(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    size: Optional[int] = None
    quality: Optional[MovieFileQuality] = None
    languages: Optional[List[Language]] = None
    mediaInfo: Optional[MovieFileMediaInfoMin] = None

    @classmethod
    def fromFull(cls, full: MovieFileFull) -> "MovieFileMin":

        return cls(
            size=full.size,
            quality=full.quality,
            languages=full.languages,
            mediaInfo=MovieFileMediaInfoMin.fromFull(full.mediaInfo)
        )

class RatingFull(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    votes: Optional[int] = None
    value: Optional[float] = None
    type: Optional[str] = None

# Rating provider mapping (replacing the Ratings class)
# The Ratings class was replaced with a dict mapping from provider name to rating

class Image(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    coverType: Optional[str] = None
    url: Optional[str] = None
    remoteUrl: Optional[str] = None

class AlternateTitle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    sourceType: Optional[str] = None
    movieMetadataId: Optional[int] = None
    title: Optional[str] = None
    id: Optional[int] = None

class RadarrStatus(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    status: Optional[str] = None  # downloaded, missing, etc
    monitored: Optional[bool] = None
    movieFileId: Optional[int] = None
    hasFile: Optional[bool] = None
    minimumAvailability: Optional[str] = None
    isAvailable: Optional[bool] = None
    tracked: Optional[bool] = None
    downloaded: Optional[bool] = None

class MovieDetailsFull(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    title: Optional[str] = None
    originalTitle: Optional[str] = None
    sortTitle: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    overview: Optional[str] = None
    inCinemas: Optional[str] = None
    physicalRelease: Optional[str] = None
    digitalRelease: Optional[str] = None
    studio: Optional[str] = None
    runtime: Optional[int] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[Any]] = None
    imdbId: Optional[str] = None
    tmdbId: Optional[int] = None
    titleSlug: Optional[str] = None
    cleanTitle: Optional[str] = None
    certification: Optional[str] = None
    hasFile: Optional[bool] = None
    path: Optional[str] = None
    folderName: Optional[str] = None
    folder: Optional[str] = None
    monitored: Optional[bool] = None
    qualityProfileId: Optional[int] = None
    website: Optional[str] = None
    remotePoster: Optional[str] = None
    youTubeTrailerId: Optional[str] = None
    originalLanguage: Optional[Language] = None
    alternateTitles: Optional[List[AlternateTitle]] = None
    secondaryYearSourceId: Optional[int] = None
    added: Optional[str] = None
    ratings: Optional[Dict[str, RatingFull]] = Field(None, description="Rating provider (e.g., 'imdb', 'tmdb', 'metacritic', 'rottenTomatoes') to rating information mapping")
    images: Optional[List[Image]] = None
    movieFile: Optional[MovieFileFull] = None
    popularity: Optional[float] = None
    radarr_status: Optional[RadarrStatus] = None

class MovieMinimal(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    title: Optional[str] = None
    year: Optional[int] = None
    tmdbId: Optional[int] = None

class QualityProfile(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    allowed_qualities: Optional[List[str]] = None


class RatingMin(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    value: Optional[float] = None
    votes: Optional[int] = None

    @classmethod
    def fromFull(cls, rating: RatingFull) -> "RatingMin":
        return cls(value=rating.value, votes=rating.votes)

class MovieDetails(BaseModel):
    """Optimized movie details model for LLM consumption, with only essential fields."""
    model_config = ConfigDict(extra="ignore")
    
    # Basic movie information
    id: Optional[int] = None
    title: Optional[str] = None
    originalTitle: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    overview: Optional[str] = None
    inCinemas: Optional[str] = None
    studio: Optional[str] = None
    runtime: Optional[int] = None
    genres: Optional[List[str]] = None
    imdbId: Optional[str] = None
    tmdbId: Optional[int] = None
    certification: Optional[str] = None
    
    # Status fields
    hasFile: Optional[bool] = None
    path: Optional[str] = None
    monitored: Optional[bool] = None
    qualityProfileId: Optional[int] = None
    
    # Simplified nested structures
    ratings: Optional[Dict[str, RatingMin]] = Field(None, description="Rating provider (e.g., 'imdb', 'tmdb') to simplified rating information mapping")
    images: Optional[List[Image]] = None
    
    # Simplified movieFile
    movieFile: Optional[MovieFileFull] = None
    
    # Additional metadata
    popularity: Optional[float] = None
    radarr_status: Optional[RadarrStatus] = None
    
    @classmethod
    def fromDetailsFull(cls, full: MovieDetailsFull) -> "MovieDetails":
        """Create a MovieDetails instance from a MovieDetailsFull object."""
        # Start with basic fields
        result = cls(
            id=full.id,
            title=full.title,
            originalTitle=full.originalTitle,
            year=full.year,
            status=full.status,
            overview=full.overview,
            inCinemas=full.inCinemas,
            studio=full.studio,
            runtime=full.runtime,
            genres=full.genres,
            imdbId=full.imdbId,
            tmdbId=full.tmdbId,
            certification=full.certification,
            hasFile=full.hasFile,
            path=full.path,
            monitored=full.monitored,
            qualityProfileId=full.qualityProfileId,
            popularity=full.popularity,
            radarr_status=full.radarr_status
        )
        
        # Convert ratings from full to minimal format
        if full.ratings:
            result.ratings = {}
            for provider, rating in full.ratings.items():
                result.ratings[provider] = RatingMin.fromFull(rating)
            
        # Handle images (if present)
        if full.images:
            result.images = full.images
            
        # Handle movieFile (if present)
        if full.movieFile:
            result.movieFile = MovieFileMin.fromFull(full.movieFile)
            
        return result