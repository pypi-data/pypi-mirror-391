from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import timedelta


class TranscriptEntry(BaseModel):
    text: str
    start: timedelta
    end: Optional[timedelta] = None
    duration: timedelta


class Transcript(BaseModel):
    video_id: str
    language: Optional[str] = None
    entries: List[TranscriptEntry] = Field(default_factory=list)


class Comments(BaseModel):
    video_id: str
    total_comments: int
    comments: List["VideoComment"] = Field(default_factory=list)


class VideoComment(BaseModel):
    video_id: str
    comment_id: str
    author: str
    text: str
    like_count: int
    published_at: str


class VideoTranscriptEntry(BaseModel):
    text: str
    start: float
    duration: float


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    publish_date: str
    channel_id: str
    channel_title: str
    tags: Optional[List[str]]


class VideoStatistics(BaseModel):
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
