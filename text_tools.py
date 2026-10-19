"""Regex sanitization, stable-sequence, and incident-index functions."""
import re
import json
import os

CONTAINER_PATTERN = r"[A-Za-z]{4}\d{7}"
SEAL_PATTERN = r"(?i)SEAL-\d{6}"
EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
INDEX_PATH = "dataset/incident-index.json"

def normalize_words(text):
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    return words

def find_longest_stable_sequence(event_codes):
    start = 0
    last_seen = {}
    best_start = 0
    best_length = 0
    
    for index, event_code in enumerate(event_codes):
        if (event_code in last_seen) and (last_seen[event_code] >= start):
            start = last_seen[event_code] + 1
        last_seen[event_code] = index
        
        current_length = index - start + 1
        if current_length > best_length:
            best_length = current_length
            best_start = start
    
    return event_codes[best_start:(best_start + best_length)]

def build_incident_index(incidents):
    index = {}
    titles = {}
    
    for incident in incidents:
        incident_id = incident["incident_id"]
        titles[incident_id] = incident["title"]
        with open(incident["report"], "r", encoding="utf-8") as file:
            report_text = file.read()
        words = normalize_words(report_text)
        
        for word in set(words):
            if incident_id not in index.setdefault(word, []):
                index[word].append(incident_id)
                
    return index, titles

def sort_incident_index(index, titles):
    sorted_index = {}
    
    for word in sorted(index):
        sorted_index[word] = sorted(index[word])
    
    sorted_titles = {}
    
    for incident_id in sorted(titles):
        sorted_titles[incident_id] = titles[incident_id]
    
    return sorted_index, sorted_titles

def save_incident_index(index, titles):
    cache = {
        "index": index,
        "titles": titles
    }
    with open(INDEX_PATH, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2)

def incident_cache_is_current(incidents):
    if not os.path.exists(INDEX_PATH):
        return False
    
    cache_modified = os.path.getmtime(INDEX_PATH)
    
    for incident in incidents:
        if os.path.getmtime(incident["report"]) > cache_modified:
            return False
    
    return True

def load_or_build_incident_index(incidents):
    if incident_cache_is_current(incidents):
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as file:
                cache = json.load(file)
            index = cache["index"]
            titles = cache["titles"]
            return index, titles
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    index, titles = build_incident_index(incidents)
    index, titles = sort_incident_index(index, titles)
    save_incident_index(index, titles)
    
    return index, titles

def search_incident_index(index, titles, query):
    query_words = set(normalize_words(query))
    scores = {}
    
    for word in query_words:
        matching_incident_ids = index.get(word, [])
        
        for incident_id in matching_incident_ids:
            scores[incident_id] = scores.get(incident_id, 0) + 1
    
    matches = []
    
    for incident_id, score in scores.items():
        if score > 0:
            matches.append({
                "incident_id": incident_id,
                "score": score,
                "title": titles[incident_id]
            })
    matches.sort(key=lambda match: (-match["score"], match["incident_id"]))
    
    return matches          