import os
from googleapiclient.discovery import build
from typing import Optional
import pickle
from yourag.core.configs.yt_config import (
    CREDENTIALS_PICKLE_FILE,
    YOUTUBE_SECRET_JSON_FILE,
    OAUTH_ENABLED,
)
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


class YouTubeClient:
    """
    This class implements a generic YouTube Data API client.
    It provides methods to interact with various YouTube Data API endpoints.
    Users Do not use this class directly; instead, use specific service classes that
    extend this generic client.
    """

    client = None

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the YouTube client with the provided API key.

        :param api_key: YouTube Data API key. If not provided, it will be read from the
                        environment variable 'YT_API_KEY'.
        """
        if not OAUTH_ENABLED:
            if self.client is not None:
                print("YouTubeClient is already initialized.")
                return  # Client already initialized

            self.api_key = api_key or os.getenv("YT_API_KEY")

            if not self.api_key:
                print("No YouTube API key provided.")
                raise ValueError(
                    "YouTube API key must be provided either as a parameter or via the 'YT_API_KEY' environment variable."
                )

            self.client = build("youtube", "v3", developerKey=self.api_key)

        else:
            try:
                self.client = self._get_authenticated_service()
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e

    def _get_authenticated_service(self):
        """
        Authenticate the user and return an authorized YouTube API client.
        """
        if os.path.exists(CREDENTIALS_PICKLE_FILE):
            with open(CREDENTIALS_PICKLE_FILE, "rb") as f:
                credentials = pickle.load(f)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_SECRET_JSON_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)
            with open(CREDENTIALS_PICKLE_FILE, "wb") as f:
                pickle.dump(credentials, f)
        return build("youtube", "v3", credentials=credentials)

    def get_video_details(self, video_id: str):
        """
        Retrieves details of a YouTube video by its ID.

        :param video_id: The ID of the YouTube video.
        :return: Video details as returned by the YouTube Data API.
        """
        return (
            self.client.videos()
            .list(part="snippet,contentDetails,statistics", id=video_id)
            .execute()
        )

    def get_channel_details(self, channel_id: str):
        """
        Retrieves details of a YouTube channel by its ID.

        :param channel_id: The ID of the YouTube channel.
        :return: Channel details as returned by the YouTube Data API.
        """
        return (
            self.client.channels()
            .list(part="snippet,contentDetails,statistics", id=channel_id)
            .execute()
        )

    def get_comments(self, video_id: str, max_results=50):
        """
        Retrieves comments for a YouTube video by its ID.

        :param video_id: The ID of the YouTube video.
        :param max_results: The maximum number of comments to retrieve.
        :return: A list of comments as returned by the YouTube Data API.
        """
        return (
            self.client.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText",
            )
            .execute()
        )

    def get_transcript(self, video_id: str):
        """
        Get the transcript of a YouTube video.

        :param video_id: The YouTube video ID.
        :return: The transcript as a list of dictionaries with start time, duration, and text
        """
        try:
            # get caption ids
            captions = (
                self.client.captions().list(part="snippet", videoId=video_id).execute()
            )
            caption_id = captions["items"][0]["id"]
            # download the captions
            transcripts = (
                self.client.captions().download(id=caption_id, tfmt="srt").execute()
            )
            return transcripts.decode("utf-8")
        except Exception as e:
            print(f"Error: {e}")
            return None

    def write_comment(self, video_id: str, text: str):
        """
        Write a comment on a YouTube video.

        :param video_id: The YouTube video ID.
        :param text: The text of the comment to post.
        :return: The posted comment as returned by the YouTube Data API.
        """
        request = self.client.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": text}},
                }
            },
        )
        response = request.execute()
        return response

    def reply_to_comment(self, comment_id: str, text: str):
        """
        Reply to a YouTube comment.

        :param comment_id: The ID of the comment to reply to.
        :param text: The text of the reply.
        """
        request = self.client.comments().insert(
            part="snippet",
            body={"snippet": {"parentId": comment_id, "textOriginal": text}},
        )
        response = request.execute()
        print("Reply posted:", response)
