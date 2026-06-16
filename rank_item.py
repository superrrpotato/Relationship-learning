import numpy as np

class RankItemEnv:
    def __init__(self, n_items: int) -> None:       
        self.n_items = n_items
        self.micro_time = 1
        self.code_book = np.eye(n_items,n_items+1)   
        self.train_pairs = [(i,j) for i in range(n_items) for j in range(n_items) if i!=j]
        self.train_labels = [1 if i<j else -1 for i,j in self.train_pairs]
        

    
    def new_pair(self):
        self.selected_pair = np.random.randint(0,len(self.train_pairs))
        self.i, self.j = self.train_pairs[self.selected_pair]
        self.label = self.train_labels[self.selected_pair]
        print('selected pairs:',self.i,self.j,"label:",self.label)



    def generate_input(self, rank_difference=None) -> np.ndarray:
        """ Generate input spikes. Meant to be called every time step.
        """
        # send oi
        if self.micro_time == 1:
            
            self.new_pair()
            print("microtime 1, send oj", self.i,flush=True)
            self.micro_time += 1
            return self.code_book[self.j]
        # send oj
        elif self.micro_time == 2:
            print("microtime 2, send oi",self.j,flush=True)
            self.micro_time += 1
            return self.code_book[self.i]
        # idle
        elif self.micro_time == 3:
            print('idle3')
            self.micro_time += 1
            return np.zeros(self.code_book.shape[1])
        elif self.micro_time == 4:
            print('idle4')
            self.micro_time += 1
            return np.zeros(self.code_book.shape[1])
        # compute and send error
        elif self.micro_time == 5:
            print("microtime 5, receive rank_difference, and send error",flush=True)
            if rank_difference!=None:
                error = self.gen_error(rank_difference)
                print("computed error:", -error, flush=True)
            else:
                error = 10
                print("set an rediculus error because no error received")
            
            self.error_input = np.zeros(self.code_book.shape[1])
            self.error_input[-1] = error 
            self.micro_time += 1
            return -self.error_input
        # send oi again to update the wrights
        elif self.micro_time == 6:
            print("microtime 6, send oi",flush=True)
            self.micro_time += 1
            return self.code_book[self.i]
        # send negative error
        elif self.micro_time == 7:
            print("microtime 7, send negative error",flush=True)
            self.micro_time += 1
            return self.error_input
        # send oj again to update the weights
        elif self.micro_time == 8:
            print("microtime 8, send oj",flush=True)
            self.micro_time = 1
            return self.code_book[self.j]
        else:
            print('error')
            return None
        
    def gen_error(self, rank_difference):
        label = self.label
        if label*rank_difference <=0:# or rank_difference==0:
            error = label
        else:
            error = 0
        # error = ((label*rank_difference-1)<0)*label
        # np.sign(np.max((label*rank_difference+1),0)*label)
        return error