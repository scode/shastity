(ns org.scode.shastity.config
  (:require [clojure.string :as string]
            [clojure.java.io :as jio]))

(def ^{:private true} *default-path* "~/.shastity/config")
(def ^{:private true} *config* (atom nil))

(defn- expand-home
  "Expand ~ to user.home, non-intelligently."
  [s]
  (string/replace s "~" (System/getProperty "user.home")))

(defn set-default-config-location
  "Set the default location of the configuration file. This is only meant to be set on
  early bootstrap or in unit tests; arbitrarly changing it during a shastity session
  is not supported. Can still be over-rodden with SHASTITY_CONFIG environment variable."
  [default-path]
  (set! *default-path* default-path))

(defn config-location
  []
  "Returns the location of the shastity configuration file. There is a default in *defualt-path* which
  can be modified using set-default-config-lcoation (but see its documentation for limitations); it
  can also be overridden using the SHASTITY_CONFIG environment variable."
  (if-let [env-path (System/getProperty "SHASTITY_CONFIG")]
    (expand-home env-path)
    (expand-home *default-path*)))

(defn read-config-file
  [path]
  (if (.exists (jio/file path))
    (with-open [r (java.io.PushbackReader. (jio/reader (jio/file path)))]
      (read r))
    {}))

(defn get-current
  "Get the currently active configuration."
  []
  (if-let [c @*config*]
    c
    (do
      (compare-and-set! *config* nil (read-config-file (default-config-location)))
      @*config*)))
