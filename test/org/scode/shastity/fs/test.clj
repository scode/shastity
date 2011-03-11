(ns org.scode.shastity.fs.test
  (:require [clojure.java.io :as io]
            [org.scode.shastity.fs :as fs])
  (:use [clojure.test]))

(deftest tempfile
  (let [tmpfile (io/as-file (fs/tempfile))]
    (is (.exists tmpfile))
    (.delete tmpfile)))

(deftest tempfile-prefix
  (let [tmpfile (io/as-file (fs/tempfile "prefix"))]
    (is (.exists tmpfile))
    (is (.startsWith (.getName tmpfile) "prefix"))
    (.delete tmpfile)))

(deftest tempfile-suffix-directory
  (let [tmpfile (io/as-file (fs/tempfile "prefix" "suffix"))]
    (is (.exists tmpfile))
    (is (.startsWith (.getName tmpfile) "prefix"))
    (is (.endsWith (.getName tmpfile) "suffix"))
    (.delete tmpfile)))

(deftest tempdir
  (let [tmpdir (io/as-file (fs/tempdir))]
    (is (.exists tmpdir))
    (.delete tmpdir)))

(deftest tempdir-prefix
  (let [tmpdir (io/as-file (fs/tempfile "prefix"))]
    (is (.exists tmpdir))
    (is (.startsWith (.getName tmpdir) "prefix"))
    (.delete tmpdir)))

(deftest tempdir-suffix-directory
  (let [tmpdir (io/as-file (fs/tempfile "prefix" "suffix"))]
    (is (.exists tmpdir))
    (is (.startsWith (.getName tmpdir) "prefix"))
    (is (.endsWith (.getName tmpdir) "suffix"))
    (.delete tmpdir)))

; TODO: Test w/ directory once we have tempdir.

(deftest with-tempfile
  (with-local-vars [path-var nil]
    (fs/with-tempfile [tmpfile]
      (is (.exists (io/as-file tmpfile)))
      (var-set path-var tmpfile))
    (is (not (.exists (io/as-file (var-get path-var)))))))

(deftest with-tempfile-args-passed
  (with-local-vars [path-var nil]
    (fs/with-tempfile [tmpfile "prefix" "suffix"]
      (is (.exists (io/as-file tmpfile)))
      (is (.startsWith (.getName (io/as-file tmpfile)) "prefix"))
      (is (.endsWith (.getName (io/as-file tmpfile)) "suffix"))
      (var-set path-var tmpfile))
    (is (not (.exists (io/as-file (var-get path-var)))))))


