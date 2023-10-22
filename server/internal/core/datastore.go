package core

var dataStore = make(map[string]*Object)
var bank float64 = 0

func NewObject(val interface{}, objType ObjectType) *Object {
	return &Object{
		Val:  val,
		Type: objType,
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
