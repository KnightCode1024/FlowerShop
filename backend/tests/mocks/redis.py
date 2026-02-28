class MockRedis:
    def __init__(self):
        self.data = {} 
    
    def pipeline(self):
        return MockPipeline(self)
    
    async def flushdb(self):
        self.data.clear()
    
    async def close(self):
        pass


class MockPipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []
        self.results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass
    
    async def zremrangebyscore(self, name, min, max):
        self.commands.append(('zremrangebyscore', name, min, max))
        return self
    
    async def zcount(self, name, min, max):
        self.commands.append(('zcount', name, min, max))
        return self
    
    async def zadd(self, name, mapping):
        self.commands.append(('zadd', name, mapping))
        return self
    
    async def expire(self, name, time):
        self.commands.append(('expire', name, time))
        return self
    
    async def execute(self):
        results = []
        
        for cmd in self.commands:
            if cmd[0] == 'zremrangebyscore':
                name, min_score, max_score = cmd[1], cmd[2], cmd[3]
                if name not in self.redis.data:
                    self.redis.data[name] = {}
                
                to_remove = []
                for member, score in self.redis.data[name].items():
                    if min_score <= score <= max_score:
                        to_remove.append(member)
                
                for member in to_remove:
                    del self.redis.data[name][member]
                
                results.append(len(to_remove))
                
            elif cmd[0] == 'zcount':
                name, min_score, max_score = cmd[1], cmd[2], cmd[3]
                if name not in self.redis.data:
                    results.append(0)
                    continue
                
                count = 0
                for score in self.redis.data[name].values():
                    if min_score <= score:
                        if max_score == "+inf" or score <= max_score:
                            count += 1
                
                results.append(count)
                
            elif cmd[0] == 'zadd':
                name, mapping = cmd[1], cmd[2]
                if name not in self.redis.data:
                    self.redis.data[name] = {}
                
                for member, score in mapping.items():
                    self.redis.data[name][member] = score
                
                results.append(len(mapping))
                
            elif cmd[0] == 'expire':
                results.append(1)
        
        return results
