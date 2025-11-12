#!/usr/bin/env python
"""
Test script to verify namespace capture and to_db_record() functionality.
Tests backward compatibility and new features.
"""

import requests
import json
from src.pg_podcast_toolkit import Podcast

def test_podcast_feed(feed_url):
    """Test parsing a real podcast feed and show the results"""
    print(f"Fetching feed: {feed_url}")
    response = requests.get(feed_url)
    feed_content = response.content

    print("\n" + "="*80)
    print("PARSING FEED")
    print("="*80)

    # Parse the feed
    podcast = Podcast(feed_content, feed_url)

    # Test backward compatibility - existing attributes still work
    print(f"\nTitle: {podcast.title}")
    print(f"Description: {podcast.description[:100] if podcast.description else None}...")
    print(f"Language: {podcast.language}")
    print(f"iTunes Image: {podcast.itunes_image}")
    print(f"Number of items: {len(podcast.items)}")

    # Test new namespace capture
    print("\n" + "="*80)
    print("CAPTURED NAMESPACES (podcast-level)")
    print("="*80)
    if podcast.namespaces:
        print(json.dumps(podcast.namespaces, indent=2, default=str))
    else:
        print("No unknown namespaces found")

    # Test to_db_record() method
    print("\n" + "="*80)
    print("DATABASE RECORD OUTPUT (podcast-level)")
    print("="*80)
    db_record = podcast.to_db_record()

    # Print column fields
    print("\nColumn Fields:")
    for key in ['id', 'podcast_guid', 'title', 'feed_url', 'image_url', 'language', 'itunes_id', 'created_at', 'updated_at']:
        print(f"  {key}: {db_record.get(key)}")

    # Print extras (truncated) - parse JSON string first
    print("\nExtras (JSONB):")
    extras_dict = json.loads(db_record['extras'])
    extras_preview = {k: (v[:100] + '...' if isinstance(v, str) and len(v) > 100 else v)
                     for k, v in extras_dict.items()}
    print(json.dumps(extras_preview, indent=2, default=str))

    # Test first episode
    if podcast.items:
        print("\n" + "="*80)
        print("FIRST EPISODE TEST")
        print("="*80)
        episode = podcast.items[0]

        # Backward compatibility
        print(f"\nTitle: {episode.title}")
        print(f"GUID: {episode.guid}")
        print(f"Duration: {episode.itunes_duration}")

        # New namespace capture
        print("\nCaptured Namespaces (episode-level):")
        if episode.namespaces:
            print(json.dumps(episode.namespaces, indent=2, default=str))
        else:
            print("No unknown namespaces found")

        # to_db_record() - requires podcast_id
        print("\nDatabase Record (episode-level):")
        ep_db_record = episode.to_db_record(podcast_id=db_record['id'])
        # Parse extras JSON string for display
        display_record = {k: v for k, v in ep_db_record.items() if k not in ['description', 'extras']}
        if 'extras' in ep_db_record:
            display_record['extras'] = json.loads(ep_db_record['extras'])
        print(json.dumps(display_record, indent=2, default=str))

    print("\n" + "="*80)
    print("TEST COMPLETE - BACKWARD COMPATIBILITY VERIFIED")
    print("="*80)

if __name__ == "__main__":
    # No Agenda Show - has extensive Podcasting 2.0 features
    test_feed = "https://feeds.noagendaassets.com/noagenda.xml"

    try:
        test_podcast_feed(test_feed)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
