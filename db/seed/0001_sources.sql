-- ============================================================
-- Parakh — launch sources seed (~20 outlets for M0)
-- IMPORTANT: ratings are OURS and NOT seeded here. Every source starts with
-- govt_alignment / ideology / factuality = NULL ("Rating pending") until the
-- §5 pipeline publishes. Do not seed ratings from mockups.
-- ============================================================

-- ---------- Ownership groups (from public/exchange filings) ----------
INSERT INTO ownership_groups (name, parent_company, owner_notes, other_holdings, evidence_source) VALUES
  ('The Times Group', 'Bennett, Coleman & Co. Ltd', 'Sahu Jain family', '["The Economic Times","Navbharat Times","Times Now","Mirror Now"]', 'from exchange filings'),
  ('AMG Media Networks', 'Adani Group', 'acquired majority stake, Dec 2022', '["Quintillion Business (BQ Prime)","IANS newswire"]', 'from exchange filings'),
  ('Network18', 'Reliance Industries', 'Independent Media Trust (Reliance)', '["CNBC-TV18","Firstpost","Moneycontrol","News18 network"]', 'from exchange filings'),
  ('HT Media', 'KK Birla group', 'Shobhana Bhartia', '["Mint","Hindustan (Hindi)","HT Smartcast"]', 'from exchange filings'),
  ('The Hindu Group', 'Kasturi & Sons Ltd', 'family-held', '["Business Line","Frontline","Sportstar"]', 'from company disclosures'),
  ('Indian Express Group', 'The Indian Express (P) Ltd', 'Viveck Goenka', '["Financial Express","Loksatta (Marathi)","Jansatta (Hindi)"]', 'from company disclosures'),
  ('India Today Group', 'Living Media India Ltd (TV Today)', 'Aroon Purie / Kalli Purie', '["Aaj Tak","Business Today","India Today TV"]', 'from exchange filings'),
  ('DB Corp', 'DB Corp Ltd', 'Agarwal family', '["Divya Bhaskar","Dainik Divya Marathi"]', 'from exchange filings'),
  ('Jagran Prakashan', 'Jagran Prakashan Ltd', 'Gupta family', '["Naidunia","Mid-Day","Radio City"]', 'from exchange filings'),
  ('Foundation for Independent Journalism', NULL, 'non-profit trust', '["The Wire Hindi","The Wire Urdu"]', 'from trust filings'),
  ('Pravda Media Foundation', NULL, 'non-profit', '[]', 'from trust filings'),
  ('BBC', 'British Broadcasting Corporation', 'UK public broadcaster', '["BBC News","BBC World Service"]', 'public record')
ON CONFLICT (name) DO NOTHING;

-- ---------- Sources ----------
-- Helper: owner() resolves an ownership group id by name.
INSERT INTO sources (name, slug, url, rss_urls, lang, ownership_group_id, is_govt_official, is_fact_checker, medium_meta) VALUES
  -- English national
  ('Times of India', 'toi', 'https://timesofindia.indiatimes.com',
     ARRAY['https://timesofindia.indiatimes.com/rssfeedstopstories.cms'], 'en',
     (SELECT id FROM ownership_groups WHERE name='The Times Group'), FALSE, FALSE, 'English · print + digital · Mumbai'),
  ('Hindustan Times', 'hindustan-times', 'https://www.hindustantimes.com',
     ARRAY['https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml'], 'en',
     (SELECT id FROM ownership_groups WHERE name='HT Media'), FALSE, FALSE, 'English · print + digital · Delhi'),
  ('The Hindu', 'the-hindu', 'https://www.thehindu.com',
     ARRAY['https://www.thehindu.com/news/national/feeder/default.rss'], 'en',
     (SELECT id FROM ownership_groups WHERE name='The Hindu Group'), FALSE, FALSE, 'English · print + digital · Chennai'),
  ('The Indian Express', 'indian-express', 'https://indianexpress.com',
     ARRAY['https://indianexpress.com/section/india/feed/'], 'en',
     (SELECT id FROM ownership_groups WHERE name='Indian Express Group'), FALSE, FALSE, 'English · print + digital · Delhi'),
  ('NDTV', 'ndtv', 'https://www.ndtv.com',
     ARRAY['https://feeds.feedburner.com/ndtvnews-top-stories'], 'en',
     (SELECT id FROM ownership_groups WHERE name='AMG Media Networks'), FALSE, FALSE, 'English · TV + digital · Delhi'),
  ('India Today', 'india-today', 'https://www.indiatoday.in',
     ARRAY['https://www.indiatoday.in/rss/home'], 'en',
     (SELECT id FROM ownership_groups WHERE name='India Today Group'), FALSE, FALSE, 'English · TV + digital · Delhi'),
  ('News18', 'news18', 'https://www.news18.com',
     ARRAY['https://www.news18.com/rss/india.xml'], 'en',
     (SELECT id FROM ownership_groups WHERE name='Network18'), FALSE, FALSE, 'English · TV + digital · Delhi'),
  ('The Wire', 'the-wire', 'https://thewire.in',
     ARRAY['https://thewire.in/rss'], 'en',
     (SELECT id FROM ownership_groups WHERE name='Foundation for Independent Journalism'), FALSE, FALSE, 'English · digital · Delhi'),
  ('Scroll.in', 'scroll', 'https://scroll.in',
     ARRAY['https://scroll.in/feeds/all.rss'], 'en', NULL, FALSE, FALSE, 'English · digital · Mumbai'),
  ('The Print', 'the-print', 'https://theprint.in',
     ARRAY['https://theprint.in/feed/'], 'en', NULL, FALSE, FALSE, 'English · digital · Delhi'),
  ('Newslaundry', 'newslaundry', 'https://www.newslaundry.com',
     ARRAY['https://www.newslaundry.com/feed'], 'en', NULL, FALSE, FALSE, 'English · digital · Delhi'),
  ('Mint', 'mint', 'https://www.livemint.com',
     ARRAY['https://www.livemint.com/rss/news'], 'en',
     (SELECT id FROM ownership_groups WHERE name='HT Media'), FALSE, FALSE, 'English · business · Delhi'),

  -- Hindi
  ('दैनिक भास्कर', 'dainik-bhaskar', 'https://www.bhaskar.com',
     ARRAY['https://www.bhaskar.com/rss-v1--category-1061.xml'], 'hi',
     (SELECT id FROM ownership_groups WHERE name='DB Corp'), FALSE, FALSE, 'हिंदी · print + digital · Bhopal'),
  ('दैनिक जागरण', 'dainik-jagran', 'https://www.jagran.com',
     ARRAY['https://www.jagran.com/rss/news/national.xml'], 'hi',
     (SELECT id FROM ownership_groups WHERE name='Jagran Prakashan'), FALSE, FALSE, 'हिंदी · print + digital · Kanpur'),
  ('आज तक', 'aaj-tak', 'https://www.aajtak.in',
     ARRAY['https://www.aajtak.in/rssfeeds/?id=home'], 'hi',
     (SELECT id FROM ownership_groups WHERE name='India Today Group'), FALSE, FALSE, 'हिंदी · TV + digital · Delhi'),
  ('BBC News हिंदी', 'bbc-hindi', 'https://www.bbc.com/hindi',
     ARRAY['https://feeds.bbci.co.uk/hindi/rss.xml'], 'hi',
     (SELECT id FROM ownership_groups WHERE name='BBC'), FALSE, FALSE, 'हिंदी · digital · London'),
  ('द वायर हिंदी', 'the-wire-hindi', 'https://thewirehindi.com',
     ARRAY['https://thewirehindi.com/feed'], 'hi',
     (SELECT id FROM ownership_groups WHERE name='Foundation for Independent Journalism'), FALSE, FALSE, 'हिंदी · digital · Delhi'),

  -- Wires
  ('Press Trust of India', 'pti', 'https://www.ptinews.com',
     ARRAY['https://www.ptinews.com/rss/national.xml'], 'en', NULL, FALSE, FALSE, 'English · wire · Delhi'),

  -- Government (labeled official; NEVER in the bias bar)
  ('Press Information Bureau', 'pib', 'https://pib.gov.in',
     ARRAY['https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3'], 'en', NULL, TRUE, FALSE, 'English · official releases · Delhi'),

  -- Fact-checkers (own content type -> fact-check chips)
  ('Alt News', 'alt-news', 'https://www.altnews.in',
     ARRAY['https://www.altnews.in/feed/'], 'en',
     (SELECT id FROM ownership_groups WHERE name='Pravda Media Foundation'), FALSE, TRUE, 'English + हिंदी · fact-check · Ahmedabad'),
  ('BOOM', 'boom-live', 'https://www.boomlive.in',
     ARRAY['https://www.boomlive.in/feed'], 'en', NULL, FALSE, TRUE, 'English + हिंदी · fact-check · Mumbai'),
  ('Newschecker', 'newschecker', 'https://newschecker.in',
     ARRAY['https://newschecker.in/feed'], 'en', NULL, FALSE, TRUE, 'multilingual · fact-check · Delhi')
ON CONFLICT (slug) DO NOTHING;
