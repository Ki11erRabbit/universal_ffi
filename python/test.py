
import uffi





args = uffi.get_arguments()


ff = uffi.ForiegnFunction('python')

a = 'test2.py' 
b = 3
c = [1,2,3]

out = ff(a, b, c)
print(out)

#print(out[3])















