(ns org.scode.shastity.persist
  (:require [org.scode.shastity.manifest :as manifest]
            [org.scode.shastity.fs :as fs]
            [org.scode.shastity.hash :as hash]
            [clojure.tools.logging :as log])
  (:import [java.nio.file Path Files]))

(defn persist-file [^Path p bs block-size]
  "Persist the file, split into blocks of block-size bytes, to the blob store.

  Return a seqable of blob hexdigests that make up the file."
  (log/infof "persisting file %s" p)
  (letfn [(upload-block [arr len]
            "Upload buffer as blob to store, returning hexdigest."
            ; todo: actually upload
            (hash/sha256-hex arr len))]
    (with-open [fin (fs/new-input-stream p)]
      (loop [block-pos 0
             block-buf (byte-array block-size)
             hexdigests []]
        (let [max-to-read (- block-size block-pos)
              rcount (.read fin block-buf block-pos max-to-read)]
          (cond
            (= rcount -1) (if (> 0 block-pos)
                            (conj hexdigests (upload-block block-buf block-pos))
                            hexdigests)
            (= rcount max-to-read) (recur 0
                                          (byte-array block-size)
                                          (conj hexdigests (upload-block block-buf
                                                                         (+ block-pos rcount))))
            :else (recur (+ block-pos rcount) block-buf hexdigests)))))))


(defn persist-dir [^Path p bs block-size]
  "Persist the given Path (p) to the blobstore (bs), and return
the hexdigest that uniquely identifies the manifest.

The side-effects of this function on the blob store are:

  - Creation of or re-use of blobs representing files.
  - Creation of or re-use of content-addressible manifest for the current path.

The process is recursive to any and all sub-directories."
  ; TODO: record ownership
  (log/infof "persisting directory %s" p)
  (with-open [entries (Files/newDirectoryStream p)]
    (let [m-entries (doall (for [entry (seq entries)]
                             (cond
                               (fs/is-symlink entry) {:type :symlink
                                                      :name (str (.getFileName (fs/to-real-no-follow entry)))
                                                      :target (str (Files/readSymbolicLink entry))}
                               (fs/is-dir entry) {:type :dir
                                                  :name (str (.getFileName (fs/to-real entry)))
                                                  :manifest (persist-dir entry bs block-size)
                                                  :mtime (fs/get-mtime entry)}
                               (fs/is-regular entry) {:type :regular
                                                      :name (str (.getFileName (fs/to-real entry)))
                                                      :blobs (persist-file entry bs block-size)
                                                      :mtime (fs/get-mtime entry)}
                               :else {:type :skip
                                      :name (str (.getFileName (fs/to-real entry)))})))
          sorted-entries (sort #(compare (:name %1) (:name %2)) m-entries)]
      ;(println sorted-entries)
      "TOOD: construct manifest")))
