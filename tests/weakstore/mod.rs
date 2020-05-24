use shastity::kv;

fn k(s: &str) -> kv::Key {
    kv::Key::new(s).unwrap()
}

pub fn test_weak_get(store: &mut dyn kv::WeakStore) {
    match store.weak_get(&k("abc")) {
        Ok(Some(_)) => panic!("store should have been empty"),
        Ok(None) => (),
        Err(e) => panic!("weak_get should have succeeded: {}", e),
    };
}

pub fn test_weak_put(store: &mut dyn kv::WeakStore) {
    match store.weak_put(&k("abc"), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("weak_put should have succeeded: {}", e),
    }

    match store.weak_get(&k("abc")) {
        Ok(Some(_)) => (),
        Ok(None) => panic!("key should have existed"),
        Err(e) => panic!("weak_get should have succeeded: {}", e),
    };
}

pub fn test_weak_exists(store: &mut dyn kv::WeakStore) {
    match store.weak_exists(&k("abc")) {
        Ok(true) => panic!("key should not have existed"),
        Ok(false) => (),
        Err(e) => panic!("weak_exists should have succeeded: {}", e),
    }

    match store.weak_put(&k("abc"), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("weak_put should have succeeded: {}", e),
    }

    match store.weak_exists(&k("abc")) {
        Ok(true) => (),
        Ok(false) => panic!("key should have existed"),
        Err(e) => panic!("weak_exists should have succeeded: {}", e),
    }
}

pub fn test_weak_delete(store: &mut dyn kv::WeakStore) {
    match store.weak_put(&k("abc"), "v".as_bytes()) {
        Ok(()) => (),
        Err(e) => panic!("weak_put should have succeeded: {}", e),
    }

    match store.weak_exists(&k("abc")) {
        Ok(true) => (),
        Ok(false) => panic!("key should have existed"),
        Err(e) => panic!("weak_exists should have succeeded: {}", e),
    }

    match store.weak_delete(&k("abc")) {
        Ok(()) => (),
        Err(e) => panic!("weak_delete should have succeeded: {}", e),
    }

    match store.weak_exists(&k("abc")) {
        Ok(true) => panic!("key should not have existed"),
        Ok(false) => (),
        Err(e) => panic!("weak_exists should not have failed: {}", e),
    }
}
