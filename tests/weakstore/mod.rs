use shastity::kv;

pub fn test_get(store: &mut kv::WeakStore) {
    match store.weak_get("test".as_bytes()) {
        Ok(Some(_)) => panic!("store should have been empty"),
        Ok(None) => (),
        Err(e) => panic!("get should not have failed: {}", e),
    };
}

pub fn test_put(store: &mut kv::WeakStore) {
    match store.weak_put("k".as_bytes(), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("put should have succeeded: {}", e),
    }

    match store.weak_get("test".as_bytes()) {
        Ok(Some(_)) => panic!("store should have been empty"),
        Ok(None) => (),
        Err(e) => panic!("get should not have failed: {}", e),
    };
}
