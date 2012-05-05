(ns org.scode.shastity.config.test
  (:require [clojure.java.io :as jio]
            [org.scode.shastity.config :as cfg]
            [org.scode.shastity.fs :as fs])
  (:use [clojure.test]))

(deftest read-config-file
  (fs/with-tempfile [p]
    (with-open [w (jio/writer (jio/file (fs/as-file p)))]
      (.write w "{ :test-key \"test-val\"}"))
    (is (= "test-val" (:test-key (cfg/read-config-file (fs/as-file p)))))))

(deftest lookup-from
  (is (= {} (cfg/lookup-from {})))
  (is (= "test-val" (cfg/lookup-from {:test-key "test-val"} :test-key)))
  (is (= "test-val" (cfg/lookup-from {:test-1 {:test-2 "test-val"}} :test-1 :test-2)))
  (is (= "test-val" (cfg/lookup-from {:test-1 {:test-2 {:test-3 "test-val"}}} :test-1 :test-2 :test-3))))
