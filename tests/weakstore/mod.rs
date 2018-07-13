use shastity::kv;

pub fn test_get(store: &mut kv::WeakStore) {
    match store.weak_get("test".as_bytes()) {
        Ok(Some(_)) => panic!("store should have been empty"),
        Ok(None) => (),
        Err(_) => panic!("get should not have failed"),
    };
}
