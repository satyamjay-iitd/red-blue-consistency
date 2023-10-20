package core

import "log"

var dataStore = make(map[string]*Object)

func NewObject(val interface{}, objType ObjectType) *Object {
	return &Object{
		Val:  val,
		Type: objType,
	}
}

func Set(key string, val *Object) {
	dataStore[key] = val
	log.Printf("%+v\n", dataStore)
}

func Get(key string) *Object {
	obj, ok := dataStore[key]
	log.Println("GET", key, obj)
	log.Printf("%+v\n", dataStore)
	if !ok {
		return nil
	}
	return obj
}
