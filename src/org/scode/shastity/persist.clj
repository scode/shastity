(ns org.scode.shastity.persist
  (:require [org.scode.shastity.manifest :as manifest]
            [org.scode.shastity.fs :as fs]
            [clojure.tools.logging :as log])
  (:import [java.nio.file Path Files]))

(defn persist-file [^Path p bs block-size]
  "Persist the file, split into blocks of block-size bytes, to the blob store.

Return a seqable of blob hexdigests that make up the file."
  (log/infof "persisting file %s" p)
  "deadbeef"; TODO: implement
  )

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
    (let [m-entries (doseq [entry (seq entries)]
                      (cond
                        (fs/is-symlink entry) {:type :symlink
                                               :name (.getFileName (fs/to-real-no-follow entry))
                                               :target (str (Files/readSymbolicLink entry))}
                        (fs/is-dir entry) {:type :dir
                                           :name (.getFileName (fs/to-real entry))
                                           :manifest (persist-dir entry bs block-size)
                                           :mtime (fs/get-mtime entry)}
                        (fs/is-regular entry) {:type :regular
                                               :name (.getFileName (fs/to-real entry))
                                               :blobs (persist-file entry bs block-size)
                                               :mtime (fs/get-mtime entry)}
                        :else {:type :skip}))]
      "TOOD: construct manifest")))

