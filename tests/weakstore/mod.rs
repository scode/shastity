use shastity::kv;

pub fn test_weak_get(store: &mut kv::WeakStore) {
    match store.weak_get("test".as_bytes()) {
        Ok(Some(_)) => panic!("store should have been empty"),
        Ok(None) => (),
        Err(e) => panic!("get should not have failed: {}", e),
    };
}

pub fn test_weak_put(store: &mut kv::WeakStore) {
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

pub fn test_weak_exists(store: &mut kv::WeakStore) {
    match store.weak_exists("k".as_bytes()) {
        Ok(true) => panic!("key should not have existed"),
        Ok(false) => (),
        Err(e) => panic!("weak_exists should not have failed: {}", e),
    }

    match store.weak_put("k".as_bytes(), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("put should have succeeded: {}", e),
    }

    match store.weak_exists("k".as_bytes()) {
        Ok(true) => (),
        Ok(false) => panic!("key should have existed"),
        Err(e) => panic!("weak_exists should not have failed: {}", e),
    }
}

pub fn test_weak_delete(store: &mut kv::WeakStore) {
    match store.weak_put("k".as_bytes(), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("put should have succeeded: {}", e),
    }

    match store.weak_exists("k".as_bytes()) {
        Ok(true) => (),
        Ok(false) => panic!("key should have existed"),
        Err(e) => panic!("weak_exists should not have failed: {}", e),
    }

    match store.weak_delete("k".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("weak_delete should have succeeded: {}", e),
    }

    match store.weak_exists("k".as_bytes()) {
        Ok(true) => panic!("key should not have existed"),
        Ok(false) => (),
        Err(e) => panic!("weak_exists should not have failed: {}", e),
    }
}
