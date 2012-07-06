(ns org.scode.shastity.fs
  (:require [clojure.java.io :as io])
  (:import [java.nio.file Path Files Paths NoSuchFileException LinkOption OpenOption]
           [java.nio.file.attribute FileAttribute FileTime]
           [java.io File]
           [java.util.concurrent TimeUnit]))

(defn as-path [^String p]
  "Given a string p, return the nio2 Path."
  (Paths/get p))

(defn as-file [^Path p]
  (.toFile p))

(defn as-string [^Path p]
  (.toString p))

(defn mkdir [^Path p]
  (Files/createDirectory p (make-array FileAttribute 0)))

(defn delete [^Path p]
  (Files/delete p))

(defn exists [^Path p]
  (Files/exists p (make-array LinkOption 0)))

(defn resolve-path [base rel]
  (.resolve base rel))

(defn to-real [^Path p]
  (.toRealPath p (make-array LinkOption 0)))

(defn to-real-no-follow [^Path p]
  (let [link-options (make-array LinkOption 1)]
    (aset link-options 0 LinkOption/NOFOLLOW_LINKS)
    (.toRealPath p link-options)))

(defn is-symlink [^Path p]
  (Files/isSymbolicLink p))

(defn is-dir [^Path p]
  (Files/isDirectory p (make-array LinkOption 0)))

(defn is-regular [^Path p]
  (Files/isRegularFile p (make-array LinkOption 0)))

(defn get-mtime [^Path p]
  "Return the mtime in nanoseconds (precision limited by OS)"
  (.to (Files/getLastModifiedTime p (make-array LinkOption 0)) (TimeUnit/NANOSECONDS)))

(defn set-mtime [^Path p nanos]
  "Set the mtime in nanoseconds (limited to OS precision)."
  (Files/setLastModifiedTime p (FileTime/from nanos (TimeUnit/NANOSECONDS))))

(defn new-input-stream [^Path p]
  (Files/newInputStream p (make-array OpenOption 0)))

(defn tempfile
  ([] (tempfile "shastity-"))
  ([prefix] (tempfile prefix nil))
  ([prefix suffix] (Files/createTempFile prefix suffix (make-array FileAttribute 0)))
  ([prefix suffix directory]
     (Files/createTempFile directory prefix suffix (make-array FileAttribute 0))))

(defn tempdir
  ([] (tempdir "shastity-"))
  ([prefix] (Files/createTempDirectory prefix (make-array FileAttribute 0)))
  ([prefix directory] (Files/createTempDirectory prefix directory (make-array FileAttribute 0))))

(defmacro with-tempfile [[path-var & rest] & body]
  "Evaluate body with a temporary file path bound to path-var; delete temporary file after
  body evaluates. The path-var will be bound to a nio2 Path instance.

  If the body deletes the file, an exception won't be thrown but the caller will have introduced
  a potential race condition. The body should only ever delete the file if done in a context where
  race conditions are not a problem."
  `(let [~path-var (tempfile ~@rest)]
    (try
      (do
        ~@body)
      (finally (try
                 (Files/delete ~path-var)
                 (catch NoSuchFileException e#))))))
