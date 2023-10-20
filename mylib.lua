#!lua name=mylib


-- Signature: FCALL accrue_interest key
local function accrue_interest(keys, args)
  local key = keys[1]
  local percentage = args[1]
  local old_val = redis.call('GET', key)

  redis.call('INCRBYFLOAT', key, old_val*percentage)

end

redis.register_function('accrue_interest', accrue_interest)
