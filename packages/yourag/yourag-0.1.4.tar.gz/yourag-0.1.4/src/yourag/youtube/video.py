from .client import YouTubeClient
from .models import (
    VideoMetadata,
    VideoStatistics,
    VideoComment,
    Comments,
    Transcript,
    TranscriptEntry,
)
import srt
from typing import Optional


class YTVideo:
    """
    Class representing a YouTube video and providing methods to retrieve its metadata,
    statistics, comments, and transcript.
    """

    def __init__(self, video_id: str, client: YouTubeClient):
        self.video_id = video_id
        self.client = client
        self._details = None

    @property
    def details(self):
        if self._details is None:
            self._details = self.client.get_video_details(self.video_id)
        return self._details

    def get_metadata(self) -> VideoMetadata:
        """
        Gets the metadata of the YouTube video.

        :return VideoMetadata: Metadata of the video.
        """
        item = self.details["items"][0]["snippet"]
        return VideoMetadata(
            video_id=self.video_id,
            title=item["title"],
            description=item.get("description"),
            publish_date=item["publishedAt"],
            channel_id=item["channelId"],
            channel_title=item["channelTitle"],
            tags=item.get("tags"),
        )

    def get_statistics(self) -> VideoStatistics:
        """
        Gets the statistics of the YouTube video.

        :return VideoStatistics: Statistics of the video.
        """
        stats = self.details["items"][0]["statistics"]
        return VideoStatistics(
            view_count=int(stats.get("viewCount", 0)),
            like_count=int(stats.get("likeCount", 0)),
            dislike_count=int(stats.get("dislikeCount", 0)),
            comment_count=int(stats.get("commentCount", 0)),
        )

    def get_comments(self, max_results=50) -> Comments:
        """
        Gets the comments of the YouTube video.

        :param max_results: Maximum number of comments to retrieve.
        :return Comments: Comments of the video.
        """
        response = self.client.get_comments(self.video_id, max_results)
        comments_list = []
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments_list.append(
                VideoComment(
                    video_id=self.video_id,
                    comment_id=item["snippet"]["topLevelComment"]["id"],
                    author=comment["authorDisplayName"],
                    text=comment["textDisplay"],
                    like_count=int(comment.get("likeCount", 0)),
                    published_at=comment["publishedAt"],
                )
            )
        total_comments = int(response["pageInfo"].get("totalResults", 0))
        return Comments(
            video_id=self.video_id,
            total_comments=total_comments,
            comments=comments_list,
        )

    def get_transcript(self) -> Transcript:
        """
        Gets the transcript of the YouTube video.

        :return: Transcript of the video.
        """
        transcript = self.client.get_transcript(self.video_id)
        transcript_parsed = srt.parse(transcript)
        transcript_list = [
            TranscriptEntry(
                text=t.content, start=t.start, end=t.end, duration=t.end - t.start
            )
            for t in transcript_parsed
        ]
        return Transcript(
            video_id=self.video_id, language="en", entries=transcript_list
        )

    def post_comment(self, text: str, comment_id: Optional[str] = None):
        """
        Posts a comment on the YouTube video. If comment_id is provided,
        it replies to that comment.

        :param text: The text of the comment to post.
        :param comment_id: The ID of the comment to reply to (if any).
        :return: The posted comment as returned by the YouTube Data API.
        """
        if comment_id:
            return self.client.reply_to_comment(comment_id, text)
        else:
            return self.client.write_comment(self.video_id, text)
