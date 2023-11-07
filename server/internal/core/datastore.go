package core

var dataStore = make(map[string]*Object)
var bank float64 = 0
var prevBank float64 = 0
var set = make(map[string]struct{})

func NewObject(val interface{}, lastSyncVal interface{}, objType ObjectType) *Object {
	return &Object{
		Val:           val,
		LastSyncedVal: lastSyncVal,
		Type:          objType,
	}
}

func Set(key string, val *Object) {
	dataStore[key] = val
}

func Get(key string) *Object {
	obj, ok := dataStore[key]
	if !ok {
		return nil
	}
	return obj
}

func flushAll() {
	dataStore = make(map[string]*Object)
	bank = 0
	prevBank = 0
	set = make(map[string]struct{})
}
