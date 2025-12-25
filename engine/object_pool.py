"""
Object pooling for efficient memory management of frequently created/destroyed objects.
"""


class ObjectPool:
    """
    Generic object pool for reusing objects instead of creating/destroying them.
    
    Usage:
        # Create a pool with a factory function
        bullet_pool = ObjectPool(lambda: Bullet(), initial_size=50)
        
        # Get an object from the pool
        bullet = bullet_pool.acquire()
        bullet.reset(x, y, velocity)  # Initialize it
        
        # Return it when done
        bullet_pool.release(bullet)
        
        # Or with context manager:
        with bullet_pool.acquire_context() as bullet:
            bullet.fire()
    """
    
    def __init__(self, factory, initial_size=10, max_size=None):
        """
        Initialize the object pool.
        
        Args:
            factory: Callable that creates new objects
            initial_size: Number of objects to pre-create
            max_size: Maximum pool size (None = unlimited)
        """
        self.factory = factory
        self.max_size = max_size
        self.available = []
        self.active = []
        
        # Pre-populate pool
        for _ in range(initial_size):
            self.available.append(factory())
    
    def acquire(self):
        """
        Get an object from the pool.
        Creates a new one if pool is empty and max_size not reached.
        
        Returns:
            Object from pool, or None if max_size reached
        """
        if self.available:
            obj = self.available.pop()
        elif self.max_size is None or len(self.active) < self.max_size:
            obj = self.factory()
        else:
            return None
        
        self.active.append(obj)
        return obj
    
    def release(self, obj):
        """
        Return an object to the pool.
        
        Args:
            obj: Object to return
        """
        if obj in self.active:
            self.active.remove(obj)
            
            # Call reset method if available
            if hasattr(obj, 'reset'):
                obj.reset()
            
            self.available.append(obj)
    
    def release_all(self):
        """Return all active objects to the pool"""
        for obj in self.active[:]:
            self.release(obj)
    
    def clear(self):
        """Clear all objects from the pool"""
        self.available.clear()
        self.active.clear()
    
    def acquire_context(self):
        """
        Context manager for automatic release.
        
        Usage:
            with pool.acquire_context() as obj:
                obj.do_something()
            # Object automatically released
        """
        return _PoolContext(self)
    
    @property
    def available_count(self):
        return len(self.available)
    
    @property
    def active_count(self):
        return len(self.active)
    
    @property
    def total_count(self):
        return len(self.available) + len(self.active)


class _PoolContext:
    """Context manager helper for ObjectPool"""
    
    def __init__(self, pool):
        self.pool = pool
        self.obj = None
    
    def __enter__(self):
        self.obj = self.pool.acquire()
        return self.obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.obj:
            self.pool.release(self.obj)
        return False


class TypedPool:
    """
    Manages multiple pools for different object types.
    
    Usage:
        pools = TypedPool()
        pools.register('bullet', Bullet, initial_size=100)
        pools.register('explosion', Explosion, initial_size=20)
        
        bullet = pools.acquire('bullet')
        pools.release('bullet', bullet)
    """
    
    def __init__(self):
        self.pools = {}
    
    def register(self, name, factory, initial_size=10, max_size=None):
        """Register a new pool type"""
        self.pools[name] = ObjectPool(factory, initial_size, max_size)
    
    def acquire(self, name):
        """Get an object from a named pool"""
        if name in self.pools:
            return self.pools[name].acquire()
        raise KeyError(f"No pool registered for '{name}'")
    
    def release(self, name, obj):
        """Return an object to a named pool"""
        if name in self.pools:
            self.pools[name].release(obj)
        else:
            raise KeyError(f"No pool registered for '{name}'")
    
    def get_pool(self, name):
        """Get a pool by name"""
        return self.pools.get(name)
    
    def stats(self):
        """Get statistics for all pools"""
        return {
            name: {
                'available': pool.available_count,
                'active': pool.active_count,
                'total': pool.total_count
            }
            for name, pool in self.pools.items()
        }

