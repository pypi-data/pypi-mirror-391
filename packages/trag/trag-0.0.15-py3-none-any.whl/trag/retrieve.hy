"
This module provides functions that generate text (markdown)
from a variety of non-plaintext sources on the web.
"

;; TODO better tool-appropriate docstrings

(require hyrule.argmove [-> ->>])

(import hyrule [inc dec])
(import hyjinx.lib [first is-url now short-id])

(import httpx)
(import json)
(import locale)
(import lxml)
(import os)
(import re)
(import subprocess)

(import lxml-html-clean [Cleaner])
(import markdownify [markdownify])
(import urllib.parse [urlparse])

(import arxiv-to-prompt [process-latex-source :as arxiv-latex])
(import arxiv [Search :as arxiv-search])
(import ddgs [DDGS])
(import wikipedia :as wiki)
(import youtube_transcript_api [YouTubeTranscriptApi])
(import youtube_transcript_api._errors [TranscriptsDisabled])
(import youtube_transcript_api.formatters [TextFormatter])

(require trag.template [deftemplate])


(deftemplate retrieval)


;; * YouTube
;; -----------------------------------------------------------------------------

(defn youtube-meta [#^ str youtube-id]
  "Return a dict of the title, author and other metadata of the youtube video."
  (let [url f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={youtube-id}&format=json"
        response (.get httpx url)]
    (match response.status-code
      200 (let [data (.json response)]
            {"title" (:title data "No title provided")
             "author" (:author-name data "No author provided")
             "version" (:version data "No version provided")
             #** data})
      otherwise (.raise_for_status response))))

(defn youtube-meta-str [#^ str youtube-id]
  "Return the title, author, version and source of the youtube video."
  (let [metadata (youtube-meta youtube-id)]
    (.join "\n" [(:title metadata) (:author metadata) (:version metadata)])))

(defn _get-transcript [#^ str youtube-id]
  "Fetch a transcript, failing gracefully where it's not available."
  (try
    (let [languages [(get (locale.getlocale) 0) "en" "en-GB"]
          ytt-api (YouTubeTranscriptApi)
          transcript-list (.list ytt-api youtube-id)
          transcript (.find-transcript transcript-list languages)
          transcript-text (.fetch transcript)
          formatter (TextFormatter)]
      (.format_transcript formatter transcript-text))
    (except [TranscriptsDisabled]
      "Transcripts are disabled for this video.")))
  
(defn get-youtube [#^ str youtube-id #^ bool [punctuate False]]
  "Load (and optionally punctuate) youtube transcript.
  Youtube 'transcripts' are normally just a long list of words with no
  punctuation or identification of the speaker.
  We can apply punctuation filter, which can give much higher quality text,
  but this takes VRAM (1-2GB) and requires pytorch.
  To do so, pass `puncuate` as `True`.
  Defaults to user's locale, this may not be desirable for summarization."
  (let [transcript (_get-transcript youtube-id)
        meta-info (youtube-meta youtube-id)]
    (when punctuate
      (do
        ; lazy import here because not everyone will want to spend the VRAM.
        (import deepmultilingualpunctuation [PunctuationModel])
        (setv transcript (.restore-punctuation (PunctuationModel) transcript))))
    {"transcript" transcript
     "accessed" (now)
     "youtube_id" youtube-id
     "version" "n/a"
     #** meta-info}))

(defn youtube [#^ str youtube-id #^ bool [punctuate False]]
  "Load (and optionally punctuate) youtube transcript as text."
  (let [ytd (get-youtube youtube-id :punctuate punctuate)]
    (retrieval "youtube" #** ytd)))


;; * Web URL and similar
;; -----------------------------------------------------------------------------

(defn get-url-raw [#^ str url]
  "Fetch a URL's content unmodified."
  (if (is-url url)
    (let [response (.get httpx url)]
      (match response.status-code
        200 response.text
        otherwise (.raise_for_status response)))
    (raise (ValueError f"Fetching {url} failed (implausible url)."))))

(defn get-url-md [#^ str url]
  "Fetch a URL's content as cleaned markdown text."
  (let [raw (get-url-raw url)
        cleaner (Cleaner :javascript True :style True)]
    (-> raw
        (lxml.html.fromstring) 
        (cleaner.clean_html)
        (lxml.html.tostring)
        (markdownify :heading-style "ATX" :strip "style")
        (.replace "\r\n" "\n")
        (.replace "\r" "\n")
        (.strip)
        (clean-web-md))))

(defn filename-from-url [#^ str url]
  "Sanitise a url into a filename."
  (let [parsed_url (urlparse url)
        netloc parsed_url.netloc
        path parsed_url.path
        fname f"{netloc}_{(os.path.basename path)}"]
    (+ (re.sub r"[^a-zA-Z0-9_.-]" "_" fname)
       "_" (short-id fname))))

(defn clean-web-md [#^ str text * [bad "#`|"]]
  "Web-sourced markdown strings often have multiple bad characters
  and repeated newlines.
  This function rewrites a string with each line stripped,
  and (stripped) lines starting with bad characters removed."
  (re.sub r"\n\n\n[\n]+" "\n" 
    (.join "\n"
      (lfor line (.split text "\n")
        ;; allow blank lines, but not 'bad' lines
        :if (if line
              (not (in (first line) bad))
              True)
          (.strip line)))))

(defn url [#^ str url]
  "Scrape a URL and return markdown text.
  
  Args:
    url: the full URL to retrieve
    
  Returns:
    sanitized markdown-formatted text of the URL's content"
  (let [data (get-url-md url)]
    (retrieval "url"
      :accessed (now)
      :url url
      :document data)))
  
  
;; * arXiv
;; ----------------------------------------------------

(defn arxiv [#^ str topic #^ int [n 20]]
  "Get `n` relevant arxiv summaries on a topic (as text)."
  (let [results (.results (arxiv-search :query topic :max-results n))
        summaries (lfor paper results
                        (let [authors (.join ", " (map str paper.authors))]
                          (retrieval "arxiv_summary"
                            :title paper.title
                            :authors authors
                            :date paper.published
                            :entry-id paper.entry-id
                            :doi paper.doi
                            :summary paper.summary)))]

    (retrieval "arxiv_search"
      :topic topic
      :summaries (.join "\n---\n" summaries))))



;; * Wikipedia
;; -----------------------------------------------------------------------------

(defn wikipedia [#^ str topic #^ int [index 0]]
  "Get the full Wikipedia page on a topic (as text).
  Disambiguates onto the first disambiguation."
  (try
    (let [pages (wiki.search topic)
          best (get pages index)
          summary (wiki.summary best :auto-suggest False)
          page (wiki.page best :auto-suggest False)]
      (retrieval "wikipedia"
        :title page.title
        :url page.url
        :content page.content
        :related (.join ", " pages)))
    (except [wiki.exceptions.DisambiguationError]
      (wikipedia topic :index (inc index)))))


;; * Miscellaneous web information
;; -----------------------------------------------------------------------------

(defn weather [#^ str [city ""]]
  "Returns current weather for a city from `wttr.in`."
  ;; move to https://open-meteo.com/
  (get-url-md f"https://wttr.in/{city}?format=2"))

(defn location []
  "Returns the user's location: city, zip, region, latitude, longitude, etc.,
  based on their IP address."
  (let [loc (-> f"http://ip-api.com/json"
                (get-url-raw)
                (json.loads))]
    (.join "\n"
      ["### Location information from http://ip-api.com:\n"
       #* (lfor [k v] (.items loc) f"    {k}: {v}")])))

(defn book-search [#^ str topic * #^ int [n 20]]
  "Returns the results of a book search.
  
  Args:
    the topic of the book search (e.g. approximate title).
    
  Returns:
    a formatted table of results."
  (with [ddgs (DDGS)]
    (let [books (cut (ddgs.books topic) n)] 
      (.join "\n\n"
             [f"Book search {topic}:"
              #* (lfor b books f"title: {(:title b)}\nauthor: {(:author b)}\npublisher: {(:publisher b)}\nurl: {(:url b)}")]))))

(defn ddg-news [#^ str topic * #^ int [n 20]]
  "Returns a web search for headline and lede of current news events.
  It is an aggregation from various news sources.
  
  Args:
    topic: the topic on which to do the search.
    
  Returns:
    a table of news headlines and ledes."
  (with [ddgs (DDGS)]
    (let [answers (cut (ddgs.news topic) n)] 
      (.join "\n\n"
             [f"News search {topic}:"
              #* (lfor a answers f"Source: {(:source a)}\nDate: {(:date a)}\nURL: {(:url a)}\nLede: {(:body a)}")]))))


;; * Shelling out
;; -----------------------------------------------------------------------------

(defn bc [#^ str expression]
  "The POSIX `bc` arbitrary precision calculator language.
  Does not know mathematical constants.
  Returns the evaluated expression"
  (let [expr (re.sub "[\"']" "" expression)
        result (subprocess.run ["bc" "-lqi"]
                               :input (.encode expr)
                               :capture-output True)
        answer (-> result.stdout (.decode) (.split) (get -1))]
    f"$ echo \"{expression}\" | bc -lqi\n{answer}"))

