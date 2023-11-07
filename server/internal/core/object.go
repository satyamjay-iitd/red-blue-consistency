package core

type ObjectType uint8

const (
	OBJ_TYPE_STRING ObjectType = iota
	OBJ_TYPE_HASH_INT
	OBJ_TYPE_HASH_FLOAT
)

type Object struct {
	Val           interface{}
	LastSyncedVal interface{} // filled only on master
	Type          ObjectType
}
