(ns org.scode.shastity.persist)

(defn persist-stream [manifest store stream size]
  "Persist the data contained in the given stream to the store, emitting an entry to the manifest. The size is
   the believed-to-be-correct size of the data, but must not necessarily match reality. (Size can be used for
   e.g. policy decisions on block size choice, but in reality streaming from a file is subject to concurrent
   writes by other processes.)"
  )
