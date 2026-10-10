\set ON_ERROR_STOP on

-- SEARCH-1 is a private, release-pinned source-exact candidate primitive.
-- The seed includes two OSHB_WORD nodes with 1 unit of segment-order distance.
DO $search1_proximity_accept$
DECLARE n integer;
BEGIN
  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','5869 a',1,1,
    'ACTION_BEFORE_TARGET',20
  );
  IF n <> 1 THEN
    RAISE EXCEPTION 'expected one anchored OSHB lemma/prefix hit, got %', n;
  END IF;

  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','5869 a',0,0,
    'ACTION_BEFORE_TARGET',20
  );
  IF n <> 0 THEN RAISE EXCEPTION 'zero-gap query must reject one intervening word'; END IF;

  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','5869 a',0,3,
    'TARGET_BEFORE_ACTION',20
  );
  IF n <> 0 THEN RAISE EXCEPTION 'wrong-direction query matched'; END IF;

  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','5869 a',1,1,
    'EITHER',20
  );
  IF n <> 1 THEN RAISE EXCEPTION 'EITHER must admit the forward hit once'; END IF;

  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','9999',0,3,
    'EITHER',20
  );
  IF n <> 0 THEN RAISE EXCEPTION 'unlisted target lemma matched'; END IF;

  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '00000000-0000-4000-8000-000000000001','7200','5869 a',0,3,
    'EITHER',20
  );
  IF n <> 0 THEN RAISE EXCEPTION 'unpublished/unpinned corpus returned candidates'; END IF;
END
$search1_proximity_accept$;

DO $search1_proximity_bad_arguments$
DECLARE failed boolean;
BEGIN
  failed := false;
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','7200','5869 a',2,1,'EITHER',20
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'reversed gap bounds were accepted'; END IF;

  failed := false;
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','7200','5869 a',0,101,'EITHER',20
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'oversized gap was accepted'; END IF;

  failed := false;
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','l/7200','5869 a',0,3,'EITHER',20
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'un-normalized source lemma input was accepted'; END IF;

  failed := false;
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','7200','5869 a',0,3,'SAME_CLAUSE',20
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'unsupported clause/query direction was accepted'; END IF;

  failed := false;
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','7200','5869 a',0,3,'EITHER',501
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'oversized page was accepted'; END IF;
END
$search1_proximity_bad_arguments$;

-- Even though the corpus is public, this internal primitive is not public SQL API.
SET ROLE anon;
DO $search1_no_public_exposure$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM * FROM publication_control.oshb_word_proximity_candidates(
      '47000000-0000-4000-8000-000000000001','7200','5869 a'
    );
  EXCEPTION WHEN insufficient_privilege THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'anon unexpectedly executed private Search1 candidate function'; END IF;
END
$search1_no_public_exposure$;
RESET ROLE;

-- A revocation is immediately effective for this evaluator, even under privileged SQL execution.
BEGIN;
SET ROLE publication_worker;
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000001',
  'REVOKED','2099-01-01T00:00:00Z','SEARCH-1 revocation negative test',NULL
);
RESET ROLE;
DO $search1_revoked$
DECLARE n integer;
BEGIN
  SELECT count(*) INTO n
  FROM publication_control.oshb_word_proximity_candidates(
    '47000000-0000-4000-8000-000000000001','7200','5869 a',0,3,'EITHER',20
  );
  IF n <> 0 THEN RAISE EXCEPTION 'REVOKED release leaked word candidates'; END IF;
END
$search1_revoked$;
ROLLBACK;
