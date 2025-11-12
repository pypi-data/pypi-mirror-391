from urllib.parse import urlparse, parse_qs


def extract_video_id(video_id_or_url: str) -> str:
    """
    Extracts the video ID from a YouTube video ID or URL.

    :param video_id_or_url: The YouTube video ID or URL.
    :return: The extracted video ID.
    """
    if len(video_id_or_url) == 11:
        return video_id_or_url
    query = urlparse(video_id_or_url)
    return parse_qs(query.query).get("v", [None])[0]
