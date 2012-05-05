(ns org.scode.shastity.fs
  (:require [clojure.java.io :as io])
  (:import [java.nio.file Path Files Paths NoSuchFileException LinkOption]
           [java.nio.file.attribute FileAttribute]
           [java.io File]))

(defn as-path [^String p]
  "Given a string p, return the nio2 Path."
  (Paths/get p))

(defn as-file [^Path p]
  (.toFile p))

(defn as-string [^Path p]
  (.toString p))

(defn delete [^Path p]
  (Files/delete p))

(defn exists [^Path p]
  (Files/exists p (make-array LinkOption 0)))

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
