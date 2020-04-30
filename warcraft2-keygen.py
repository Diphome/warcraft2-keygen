
import random, time

start_time = time.time()

full_array = [255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,0,255,1,255,2,3,4,5,255,255,255,255,255,
255,255,255,6,7,8,9,10,11,12,255,13,14,255,15,16,255,
17,255,18,255,19,255,20,21,22,255,23,255,255,255,255,
255,255,255,6,7,8,9,10,11,12,255,13,14,255,15,16,255,
17,255,18,255,19,255,20,21,22,255,23,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255]

authorized_chars = ['2', '4', '6', '7', '8', '9',
 'B', 'C', 'D', 'E', 'F', 'G', 'H',
 'J', 'K', 'M', 'N', 'P', 'R', 'T',
 'V', 'W', 'X', 'Z', 'b', 'c', 'd',
 'e', 'f', 'g', 'h', 'j', 'k', 'm',
 'n', 'p', 'r', 't', 'v', 'w', 'x',
 'z']

def validate_char_in_key(key):
  for c in key:
    if c not in authorized_chars:
        print c
        print "key rejected unauthorized char"
        break

def calculus_01(letter, debug=False):
  if debug:
    print 'letter : ' + letter
  v1 = letter.lower() #If the letter was a maj put it into lowercase
  if(ord(v1) < 97): 
    result = ord(v1) - 48 #If it's a number we substract 48
  else:
    result = ord(v1) - 87 #If it's not a number we substract 87
  if debug:
    print 'result : ' + str(result)
  return result

def calculus_02(a1, debug=False):
  if debug:
    print 'a1 : ' + str(a1)
  v1 = a1 & 15
  if ( v1 < 10 ):
    result = v1 + 48
  else:
    result = v1 + 55
  if debug:
    print 'result : ' + str(result)
  return result

def validate_key(CDKEY):
  #-------------------------------------------------------------------------
  #Getting the first score and a new key generated from the given key.
  #-------------------------------------------------------------------------
  result = 0
  new_key_decimal = []
  counter=0 # representera l'offset de notre char
  v2 = 1
  principal_key_score = 0 
  v4 = 0

  '''
  Simple check to ensure CDKEY contains only specifics characters.
  '''
  validate_char_in_key(CDKEY)

  '''
  First loop in which a key is generated using values from inputed CDKEY
  and a score is stored
  '''
  for i in range(0,8): #Since we move on a 2 step, we have to go until key length divided by 2.

    '''
    Calculation of the principal_key_score
    '''
    v4 = 3*full_array[ord(CDKEY[counter])] # 
    v5 = full_array[ord(CDKEY[counter+1])] + 8 * v4

    if (v5 >= 256):
      v5 -= 256
      principal_key_score = principal_key_score | v2 + principal_key_score #inclusive OR, the result is added in the first operand.

    '''
    Generation of the new_key
    '''
    new_key_decimal.append(calculus_02(v5 >> 4)) #If v5 >= 16 calculus_02 will take 1 as parameter. 
    result = calculus_02(v5 & 15) # V5 should be 0xF (15) here and result 0x46 (70)
    new_key_decimal.append(result)
    counter = counter + 2
    v2 = v2*2

  '''
  Now we have the decimal array, we just have to convert it into
  chars to get the new key.
  '''
  new_key = ''
  for c in new_key_decimal:
    new_key = new_key + chr(c)

  print 'Using given key   : ' + CDKEY
  print 'Generated key is  : ' + new_key

  #-------------------------------------------------------------------------
  #Getting the second score using the new_key_decimal generated.
  #-------------------------------------------------------------------------
  v4 = 3 
  counter = 0
  key_score = 0

  for value in CDKEY:
    v6 = chr(new_key_decimal[counter])
    #Condition to check that each character of our CDKEY is in ascii 0-9,a-z,A-Z.
    if ( (v6 < '0' or v6 > '9') and (v6 < 'a' or v6 > 'z') and (v6 < 'A' or v6 > 'Z') ):
      print "key rejected unauthorized char"
      break
    v4 = v4 + ( 2 * v4 ^ calculus_01(v6) ) #Get v4 new value.
    counter = counter + 1 #We pass to next char.
  key_score = v4 & 255

  print 'Get CDKEY score            : ' + str(principal_key_score)
  print 'Get generated key score : ' + str(key_score)

  if(principal_key_score == key_score):
    print 'Key is valid'
    return 1
  else:
    print 'key rejected'
    return 0
  #-------------------------------------------------------------------------

def generate_random_key():
  random_key = ''
  for i in range(0, 16):
    random_key = random_key + random.choice(authorized_chars)
  return random_key

failure_counter = 0

CDKEY=generate_random_key()
while (validate_key(CDKEY) != 1):
  failure_counter = failure_counter +1
  CDKEY=generate_random_key()

print('found valid key in {} seconds  after {} failures'.format((time.time() - start_time),failure_counter))
print('key is : ' + CDKEY)