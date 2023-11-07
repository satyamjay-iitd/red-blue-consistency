#!lua name=mylib


-- Signature: FCALL accrue_interest key
local function accrue_interest(keys, args)
  local key = keys[1]
  local percentage = args[1]
  local old_val = redis.call('GET', key)

  if not old_val then
    old_val = 0
  else
    old_val = tonumber(old_val)
  end

  redis.call('INCRBYFLOAT', key, old_val*percentage)

end

-- Signature: FCALL deposit key
local function withdraw(keys, args)
  local key = keys[1]
  local amount = tonumber(args[1])
  local old_val = redis.call('GET', key)

  if not old_val then
    old_val = 0
  else
    old_val = tonumber(old_val)
  end

  if old_val <= amount then
    old_val = old_val - amount
  end

  redis.call('SET', key, old_val)

end

redis.register_function('accrue_interest', accrue_interest)
redis.register_function('withdraw', withdraw)
