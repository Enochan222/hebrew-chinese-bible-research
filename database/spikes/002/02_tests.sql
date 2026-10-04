\set ON_ERROR_STOP on

DO $whole_bible$
DECLARE
  n bigint;
BEGIN
  SELECT count(*) INTO n FROM authoring.biblical_books;
  IF n <> 39 THEN
    RAISE EXCEPTION 'expected 39 OSHB provider book divisions, got %', n;
  END IF;

  SELECT count(*) INTO n FROM authoring.reference_labels;
  IF n < 20000 THEN
    RAISE EXCEPTION 'whole-Bible reference coverage unexpectedly small: %', n;
  END IF;

  SELECT count(*) INTO n FROM authoring.text_segments;
  IF n < 300000 THEN
    RAISE EXCEPTION 'whole-Bible word coverage unexpectedly small: %', n;
  END IF;

  IF EXISTS (
    SELECT 1
    FROM authoring.biblical_books b
    LEFT JOIN authoring.reference_labels l ON l.book_id = b.book_id
    GROUP BY b.book_id
    HAVING count(l.reference_label_id) = 0
  ) THEN
    RAISE EXCEPTION 'at least one imported book has no reference labels';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM authoring.analysis_nodes node
    LEFT JOIN authoring.analysis_node_segments ns ON ns.analysis_node_id = node.analysis_node_id
    GROUP BY node.analysis_node_id
    HAVING count(ns.text_segment_id) <> 1
  ) THEN
    RAISE EXCEPTION 'an OSHB morphology node does not have exactly one text-segment membership';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM authoring.text_segments seg
    LEFT JOIN authoring.analysis_node_segments ns ON ns.text_segment_id = seg.text_segment_id
    GROUP BY seg.text_segment_id
    HAVING count(ns.analysis_node_id) <> 1
  ) THEN
    RAISE EXCEPTION 'an imported OSHB text segment does not have exactly one morphology node';
  END IF;

  SELECT count(*) INTO n
  FROM authoring.analysis_node_features
  WHERE feature_key = 'provider_word_id';
  IF n <> (SELECT count(*) FROM authoring.analysis_nodes) THEN
    RAISE EXCEPTION 'provider_word_id feature coverage mismatch';
  END IF;

  IF (
    SELECT count(DISTINCT feature_value)
    FROM authoring.analysis_node_features
    WHERE feature_key = 'provider_word_id'
  ) <> (SELECT count(*) FROM authoring.analysis_nodes) THEN
    RAISE EXCEPTION 'provider_word_id is not unique across imported OSHB nodes';
  END IF;

  SELECT count(*) INTO n
  FROM authoring.text_segments s
  JOIN authoring.reference_spans rs ON rs.reference_span_id = s.reference_span_id
  JOIN authoring.reference_label_members rlm ON rlm.reference_atom_id = rs.start_atom_id
  JOIN authoring.reference_labels rl ON rl.reference_label_id = rlm.reference_label_id
  WHERE rl.label = '1Sam.16.7';
  IF n <> 25 THEN
    RAISE EXCEPTION '1Sam.16.7 OSHB canary expected 25 words, got %', n;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM authoring.reference_labels WHERE label='Gen.1.1') THEN
    RAISE EXCEPTION 'Gen.1.1 missing from whole-Bible import';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM authoring.reference_labels WHERE label='Mal.4.6') THEN
    RAISE EXCEPTION 'Mal.4.6 missing from whole-Bible import';
  END IF;
END
$whole_bible$;
