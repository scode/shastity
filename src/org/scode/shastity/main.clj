(ns org.scode.shastity.main
  (:gen-class)
  (:require [org.scode.shastity.config :as cfg]
            [org.scode.shastity.persist :as persist]
            [org.scode.shastity.fs :as fs]
            [org.scode.shastity.blobstore.s3]
            [clojure.tools.logging :as log]
            [clojure.tools.cli :as cli])
  (:import [com.amazonaws.services.s3 AmazonS3Client]
           [com.amazonaws.auth BasicAWSCredentials]))

(defn- open-s3-store [name]
  (let [access-key (cfg/lookup :stores (keyword name) :access-key)
        secret-key (cfg/lookup :stores (keyword name) :secret-key)
        bucket-name (cfg/lookup :stores (keyword name) :bucket)
        bucket-path (cfg/lookup :stores (keyword name) :path)
        s3-client (AmazonS3Client. (BasicAWSCredentials. access-key secret-key))]
    (org.scode.shastity.blobstore.s3.S3Store. s3-client bucket-name bucket-path)))

(defn- cmd-persist [opts [src-path dst-store]]
  ; TODO: do not hard-code block size
  (let [store (open-s3-store dst-store)
        root-manifest (persist/persist-dir (fs/as-path src-path) store (* 1 1024 1024))]
    (log/logf "persisted as %s" root-manifest)))

(defn -main [& args]
  ; TODO: Support real commands. For now we absolutely require that the first parameter is the
  ; command, and we don't support per-command arguments.
  ; TODO: don't bail with random exception if cmd isn't given
  (let [cmd (first args)
        [opts, args] (cli/cli (rest args))]
    (case cmd
      "persist" (cmd-persist opts args))))
