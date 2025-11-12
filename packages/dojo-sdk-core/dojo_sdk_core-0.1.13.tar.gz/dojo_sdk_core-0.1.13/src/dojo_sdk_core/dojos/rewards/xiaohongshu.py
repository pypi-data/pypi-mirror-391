"""
Reward functions for Xiaohongshu (Little Red Book) app tasks.
"""

import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _find_post(final_state: Dict[str, Any], post_id: str) -> Tuple[Optional[Dict[str, Any]], str]:
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return None, "Posts array missing in final state"
    for post in posts:
        if post.get("id") == post_id:
            return post, ""
    return None, f"Post with id '{post_id}' not found in final state"


def _find_user(final_state: Dict[str, Any], user_id: str) -> Tuple[Optional[Dict[str, Any]], str]:
    users = final_state.get("users")
    if not isinstance(users, list):
        return None, "Users array missing in final state"
    for user in users:
        if user.get("id") == user_id:
            return user, ""
    return None, f"User with id '{user_id}' not found in final state"


def _get_current_user(final_state: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    current_user = final_state.get("currentUser")
    if not isinstance(current_user, dict):
        return None, "currentUser object missing in final state"
    return current_user, ""


def _validate_single_comment(
    post: Dict[str, Any], expected_text: str, *, expected_author: Optional[str] = None
) -> Tuple[bool, str]:
    comments = post.get("comments")
    if not isinstance(comments, list):
        return False, f"Post {post.get('id')} comments array missing"
    if len(comments) != 1:
        return False, f"Post {post.get('id')} has {len(comments)} comments, expected 1"
    comment = comments[0]
    content = comment.get("content", "")
    if expected_text.lower() not in content.lower():
        return False, f"Post {post.get('id')} comment content '{content}' missing '{expected_text}'"
    if expected_author is not None and comment.get("authorId") != expected_author:
        return False, f"Post {post.get('id')} comment authorId={comment.get('authorId')} expected {expected_author}"
    return True, ""


def _check_exact_list(values: Any, expected: Tuple[str, ...], field_name: str) -> Tuple[bool, str]:
    if not isinstance(values, list):
        return False, f"{field_name} is not a list"
    if len(values) != len(expected):
        return False, f"{field_name} has length {len(values)}, expected {len(expected)}"
    if sorted(values) != sorted(expected):
        return False, f"{field_name}={values} does not match expected {list(expected)}"
    return True, ""


def _validate_bookmarkpost(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error

    ok, error = _check_exact_list(current_user.get("bookmarks"), ("1",), "currentUser.bookmarks")
    if not ok:
        return 0.0, error

    post, error = _find_post(final_state, "1")
    if not post:
        return 0.0, error
    if post.get("bookmarks") != 1:
        return 0.0, f"Post 1 bookmarks={post.get('bookmarks')} expected 1"

    user, error = _find_user(final_state, "1")
    if not user:
        return 0.0, error
    if user.get("bookmarkedCount") != 1:
        return 0.0, f"User 1 bookmarkedCount={user.get('bookmarkedCount')} expected 1"

    return 1.0, "Post 1 bookmarked and counts updated"


def _validate_commentontwoseparateposts(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post1, error = _find_post(final_state, "1")
    if not post1:
        return 0.0, error
    ok, error = _validate_single_comment(post1, "nice song!")
    if not ok:
        return 0.0, error

    post2, error = _find_post(final_state, "2")
    if not post2:
        return 0.0, error
    ok, error = _validate_single_comment(post2, "what the dog doing?")
    if not ok:
        return 0.0, error

    if final_state.get("page") != "explore":
        return 0.0, f"page is {final_state.get('page')} expected 'explore'"

    return 1.0, "Posted correct comments on posts 1 and 2 while staying on explore page"


def _validate_commentonvideo(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post, error = _find_post(final_state, "4")
    if not post:
        return 0.0, error
    ok, error = _validate_single_comment(post, "this cat so cute!", expected_author="0")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully commented 'this cat so cute!' on post 4"


def _validate_comprehensiveuserinteraction(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page is {final_state.get('page')} expected 'explore'"

    post1, error = _find_post(final_state, "1")
    if not post1:
        return 0.0, error
    if post1.get("likes") != 1:
        return 0.0, f"Post 1 likes={post1.get('likes')} expected 1"
    ok, error = _validate_single_comment(post1, "nice")
    if not ok:
        return 0.0, error

    post2, error = _find_post(final_state, "2")
    if not post2:
        return 0.0, error
    if post2.get("likes") != 1 or post2.get("bookmarks") != 1:
        return 0.0, f"Post 2 likes={post2.get('likes')} bookmarks={post2.get('bookmarks')} expected 1/1"

    post7, error = _find_post(final_state, "7")
    if not post7:
        return 0.0, error
    if post7.get("likes") != 1:
        return 0.0, f"Post 7 likes={post7.get('likes')} expected 1"

    user1, error = _find_user(final_state, "1")
    if not user1:
        return 0.0, error
    if user1.get("likeCount") != 1:
        return 0.0, f"User 1 likeCount={user1.get('likeCount')} expected 1"

    user2, error = _find_user(final_state, "2")
    if not user2:
        return 0.0, error
    if user2.get("likeCount") != 2 or user2.get("bookmarkedCount") != 1:
        return 0.0, (
            f"User 2 likeCount={user2.get('likeCount')} bookmarkedCount={user2.get('bookmarkedCount')} expected 2/1"
        )

    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, error = _check_exact_list(current_user.get("likedPosts"), ("1", "2", "7"), "currentUser.likedPosts")
    if not ok:
        return 0.0, error
    ok, error = _check_exact_list(current_user.get("following"), ("2",), "currentUser.following")
    if not ok:
        return 0.0, error

    return 1.0, "Completed comprehensive multi-post interaction requirements"


def _validate_crossuserengagement(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post_ids = {
        "1": {"likes": 1},
        "2": {"likes": 1, "bookmarks": 1},
        "3": {"likes": 1},
        "4": {"likes": 1, "bookmarks": 1},
        "5": {"likes": 1},
    }

    for pid, expectations in post_ids.items():
        post, error = _find_post(final_state, pid)
        if not post:
            return 0.0, error
        for field, expected_value in expectations.items():
            if post.get(field) != expected_value:
                return 0.0, f"Post {pid} {field}={post.get(field)} expected {expected_value}"

    post3, _ = _find_post(final_state, "3")
    ok, error = _validate_single_comment(post3, "nice")
    if not ok:
        return 0.0, error

    post4, _ = _find_post(final_state, "4")
    ok, error = _validate_single_comment(post4, "meow")
    if not ok:
        return 0.0, error

    user5, error = _find_user(final_state, "5")
    if not user5:
        return 0.0, error
    followers = user5.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"User 5 followers={followers} expected to include '0'"

    if final_state.get("page") != "profile" or final_state.get("profileUserId") != "5":
        return 0.0, (
            f"page={final_state.get('page')} profileUserId={final_state.get('profileUserId')} expected profile/5"
        )

    return 1.0, "Completed cross-user engagement interactions and viewed user 5 profile"


def _validate_follownavigatehome(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    following = current_user.get("following")
    if not isinstance(following, list) or "2" not in following:
        return 0.0, f"currentUser.following={following} expected to include '2'"

    user2, error = _find_user(final_state, "2")
    if not user2:
        return 0.0, error
    followers = user2.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"User 2 followers={followers} expected to include '0'"

    if final_state.get("page") != "explore":
        return 0.0, f"page is {final_state.get('page')} expected 'explore'"

    return 1.0, "Followed user 2 and returned to explore page"


def _validate_followuser(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, err = _check_exact_list(current_user.get("following"), ("1",), "currentUser.following")
    if not ok:
        return 0.0, err

    user1, error = _find_user(final_state, "1")
    if not user1:
        return 0.0, error
    ok, err = _check_exact_list(user1.get("followers"), ("0",), "User 1 followers")
    if not ok:
        return 0.0, err

    return 1.0, "Successfully followed user 1"


def _validate_like3sequential(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    for pid in ("1", "2", "3"):
        post, error = _find_post(final_state, pid)
        if not post:
            return 0.0, error
        if post.get("likes") != 1:
            return 0.0, f"Post {pid} likes={post.get('likes')} expected 1"

    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, err = _check_exact_list(current_user.get("likedPosts"), ("1", "2", "3"), "currentUser.likedPosts")
    if not ok:
        return 0.0, err

    for uid in ("1", "2", "3"):
        user, error = _find_user(final_state, uid)
        if not user:
            return 0.0, error
        if user.get("likeCount") != 1:
            return 0.0, f"User {uid} likeCount={user.get('likeCount')} expected 1"

    return 1.0, "Sequentially liked posts 1, 2, and 3"


def _validate_likeandbookmark(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post, error = _find_post(final_state, "2")
    if not post:
        return 0.0, error
    if post.get("likes") != 1 or post.get("bookmarks") != 1:
        return 0.0, f"Post 2 likes={post.get('likes')} bookmarks={post.get('bookmarks')} expected 1/1"

    user2, error = _find_user(final_state, "2")
    if not user2:
        return 0.0, error
    if user2.get("likeCount") != 1 or user2.get("bookmarkedCount") != 1:
        return 0.0, (
            f"User 2 likeCount={user2.get('likeCount')} bookmarkedCount={user2.get('bookmarkedCount')} expected 1/1"
        )

    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, err = _check_exact_list(current_user.get("likedPosts"), ("2",), "currentUser.likedPosts")
    if not ok:
        return 0.0, err
    ok, err = _check_exact_list(current_user.get("bookmarks"), ("2",), "currentUser.bookmarks")
    if not ok:
        return 0.0, err

    return 1.0, "Liked and bookmarked post 2 with correct counts"


def _validate_likepost(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post, error = _find_post(final_state, "1")
    if not post:
        return 0.0, error
    if post.get("likes") != 1:
        return 0.0, f"Post 1 likes={post.get('likes')} expected 1"

    user1, error = _find_user(final_state, "1")
    if not user1:
        return 0.0, error
    if user1.get("likeCount") != 1:
        return 0.0, f"User 1 likeCount={user1.get('likeCount')} expected 1"

    return 1.0, "Liked post 1"


def _validate_navigateownprofile(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page is {final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Navigated to current user's profile"


def _validate_openpostmodal(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if not final_state.get("activePostId"):
        return 0.0, "activePostId is missing or null"
    if final_state.get("isVideoPaused") is True:
        return 0.0, "isVideoPaused is True; expected False while modal open"
    return 1.0, "Opened a post modal with video playing"


def _validate_openvideopause(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused after opening post 2"
    return 1.0, "Opened post 2 video and paused it"


def _validate_searchandfollowall(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, err = _check_exact_list(
        current_user.get("following"),
        ("1", "2", "3", "4", "5"),
        "currentUser.following",
    )
    if not ok:
        return 0.0, err

    for uid in ("1", "2", "3", "4", "5"):
        user, error = _find_user(final_state, uid)
        if not user:
            return 0.0, error
        followers = user.get("followers")
        if not isinstance(followers, list) or "0" not in followers:
            return 0.0, f"User {uid} followers={followers} expected to include '0'"

    if final_state.get("page") != "explore":
        return 0.0, f"page is {final_state.get('page')} expected 'explore'"

    return 1.0, "Followed all users 1-5 and returned to explore"


def _validate_search_and_like(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post, error = _find_post(final_state, "1")
    if not post:
        return 0.0, error
    if post.get("likes") != 1:
        return 0.0, f"Post 1 likes={post.get('likes')} expected 1"

    user1, error = _find_user(final_state, "1")
    if not user1:
        return 0.0, error
    if user1.get("likeCount") != 1:
        return 0.0, f"User 1 likeCount={user1.get('likeCount')} expected 1"

    return 1.0, "Searched and liked post 1"


def _validate_search_input(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("searchQuery") != "hello":
        return 0.0, f"searchQuery={final_state.get('searchQuery')} expected 'hello'"
    return 1.0, "Updated search input to 'hello'"


def _validate_searchuserandlikeall(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    target_posts = ("2", "7", "12", "17")
    for pid in target_posts:
        post, error = _find_post(final_state, pid)
        if not post:
            return 0.0, error
        if post.get("likes") != 1:
            return 0.0, f"Post {pid} likes={post.get('likes')} expected 1"

    user2, error = _find_user(final_state, "2")
    if not user2:
        return 0.0, error
    if user2.get("likeCount") != 4:
        return 0.0, f"User 2 likeCount={user2.get('likeCount')} expected 4"

    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    ok, err = _check_exact_list(current_user.get("likedPosts"), target_posts, "currentUser.likedPosts")
    if not ok:
        return 0.0, err

    return 1.0, "Liked all posts from user 2"


def _validate_unfollowuser(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    following = current_user.get("following")
    if not isinstance(following, list) or len(following) != 0:
        return 0.0, f"currentUser.following={following} expected empty list"

    user1, error = _find_user(final_state, "1")
    if not user1:
        return 0.0, error
    followers = user1.get("followers")
    if not isinstance(followers, list) or len(followers) != 0:
        return 0.0, f"User 1 followers={followers} expected empty list"

    if final_state.get("page") != "profile" or final_state.get("profileUserId") != "1":
        return 0.0, (
            f"page={final_state.get('page')} profileUserId={final_state.get('profileUserId')} expected profile/1"
        )

    return 1.0, "Successfully unfollowed user 1 while viewing their profile"


def _validate_unlikepost(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    post, error = _find_post(final_state, "10")
    if not post:
        return 0.0, error
    if post.get("likes") != 0:
        return 0.0, f"Post 10 likes={post.get('likes')} expected 0"

    current_user, error = _get_current_user(final_state)
    if not current_user:
        return 0.0, error
    liked_posts = current_user.get("likedPosts")
    if not isinstance(liked_posts, list) or len(liked_posts) != 0:
        return 0.0, f"currentUser.likedPosts={liked_posts} expected empty list"

    return 1.0, "Unliked post 10 and cleared likedPosts"


def _validate_watchfullvideo(initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused at completion"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching video"
    return 1.0, "Watched post 2 video through completion"


# Registry of all Xiaohongshu reward functions
REWARD_FUNCTIONS_XIAOHONGSHU = {
    "_validate_bookmarkpost": _validate_bookmarkpost,
    "_validate_commentontwoseparateposts": _validate_commentontwoseparateposts,
    "_validate_commentonvideo": _validate_commentonvideo,
    "_validate_comprehensiveuserinteraction": _validate_comprehensiveuserinteraction,
    "_validate_crossuserengagement": _validate_crossuserengagement,
    "_validate_follownavigatehome": _validate_follownavigatehome,
    "_validate_followuser": _validate_followuser,
    "_validate_like3sequential": _validate_like3sequential,
    "_validate_likeandbookmark": _validate_likeandbookmark,
    "_validate_likepost": _validate_likepost,
    "_validate_navigateownprofile": _validate_navigateownprofile,
    "_validate_openpostmodal": _validate_openpostmodal,
    "_validate_openvideopause": _validate_openvideopause,
    "_validate_searchandfollowall": _validate_searchandfollowall,
    "_validate_search_and_like": _validate_search_and_like,
    "_validate_search_input": _validate_search_input,
    "_validate_searchuserandlikeall": _validate_searchuserandlikeall,
    "_validate_unfollowuser": _validate_unfollowuser,
    "_validate_unlikepost": _validate_unlikepost,
    "_validate_watchfullvideo": _validate_watchfullvideo,
}
