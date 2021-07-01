(ns humbug-demo
  (:import (dev.bugout.humbug HumbugConsent ConsentMechanism Reporter)))

(def consent (HumbugConsent. true))                         ;Consent with boolean
(println (.check consent))

(defn functional_mechanism [f]                              ;ConsentMechanism constructor
  (reify
    ConsentMechanism
    (call [this] (f))
    )
  )

(def demo-mechanism (functional_mechanism (fn [] true)))    ;ConsentMechanism examples
(def demo-mechanism2 (functional_mechanism
                       (fn []
                         (true? true)
                         ))
  )

(def consent-functional (HumbugConsent. (into-array (list demo-mechanism demo-mechanism2))))
                                                            ;Consent with functions


(println (.check consent-functional))

(def TOKEN "95cfa467-94ae-4891-951b-7874d6a13e2c")
(def reporter (Reporter. "clojure reporter" consent "300" "300" TOKEN))
(def tags  (into-array (list "clojure" "test")))

(.systemReport reporter tags)                               ;Reporting system information

(try
  (/ 1 0)
  (catch Exception e (.errorReport reporter e tags)))       ;Exception reporting

(try
  (throw (Exception. "exception"))
  (catch Exception e (.errorReport reporter e tags)))

(try
  (throw
    (ex-info "The ice cream has melted!"
             {:causes             #{:fridge-door-open :dangerously-high-temperature}
              :current-temperature {:value 25 :unit :celsius}}))
  (catch Exception e (.errorReport reporter e tags)))

(.customReport reporter "Clojure" "Hello from clojure" tags) ;Custom reporting