#!/usr/bin/env python3
#-*- coding: utf-8 -*-

class Constraint:
    def __init__(self): pass
    def process_new_value(self): pass
    def process_forget_value(self): pass

class Connector:
    def __init__(self):
        self.value = None
        self.informant = None
        self.constraints = []

    @staticmethod
    def for_each_except(exception, bln, items):
        for item in items:
            if item != exception:
                if bln:
                    item.process_new_value()
                else:
                    item.process_forget_value()
        return 'done'

    @property
    def has_value(self):
        return self.informant != None
    
    def set_value(self, newval, setter):
        if not self.has_value:
            self.value = newval
            self.informant = setter
            return self.for_each_except(setter, True, self.constraints)
        if self.value != newval:
            raise Exception('Contradiction {0}, {1}'.format(self.value, newval))
        return 'ignored'
    
    def forget_value(self, retractor):
        if retractor == self.informant:
            self.informant = None
            return self.for_each_except(
                retractor, False, self.constraints)
        return 'ignored'
    
    def connect(self, constraint):
        try:
            self.constraints.index(constraint)
        except:
            self.constraints.insert(0, constraint)
        if self.has_value:
            constraint.process_new_value()
        return 'done'
    def probe(self, name):
        p = Probe(name, self)
        self.connect(p)

    @staticmethod
    def cv(value):
        c = Connector()
        Constant(value, c)
        return c

    def __add__(self, y):
        z = Connector()
        Adder(self, y, z)
        return z

    def __sub__(self, y):
        z = Connector()
        Adder(y, z, self)
        return z

    def __mul__(self, y):
        z = Connector()
        Multiplier(self, y, z)
        return z

    def __truediv__(self, y):
        z = Connector()
        Multiplier(y, z, self)
        return z

    def celsius_fahrenheit_converter(self):
        return self.cv(9) / self.cv(5) * self + self.cv(32)

class Probe(Constraint):
    def __init__(self, name, connector):
        self.name = name
        self.connector = connector
        
    def print_probe(self, value):
        print('Probe: {0} = {1}'.format(self.name, value))
        
    def process_new_value(self):
        self.print_probe(self.connector.value)
        
    def process_forget_value(self):
        self.print_probe('?')

class Constant(Constraint):
    def __init__(self, value, connector):
        self.connector = connector
        self.connector.connect(self)
        self.connector.set_value(value, self.connector)
    def __str__(self):
        return '定数: {0}'.format(self.value)

class Adder(Constraint):
    def __init__(self, a1, a2, s):
        self.a1 = a1
        self.a2 = a2
        self.s = s
        self.a1.connect(self)
        self.a2.connect(self)
        self.s.connect(self)
    def process_new_value(self):
        if self.a1.has_value and self.a2.has_value:
            self.s.set_value(self.a1.value + self.a2.value, self)
        elif self.a1.has_value and self.s.has_value:
            self.a2.set_value(self.s.value - self.a1.value, self)
        elif self.a2.has_value and self.s.has_value:
            self.a1.set_value(self.s.value - self.a2.value, self)
    def process_forget_value(self):
        self.s.forget_value(self)
        self.a1.forget_value(self)
        self.a2.forget_value(self)
        self.process_new_value()
    def __str__(self):
        return '{0} + {1} = {2}'.format(
            self.a1.value, self.a2.value, self.s.value)

class Multiplier(Constraint):
    def __init__(self, m1, m2, product):
        self.m1 = m1
        self.m2 = m2
        self.product = product
        self.m1.connect(self)
        self.m2.connect(self)
        self.product.connect(self)
    def process_new_value(self):
        if  (self.m1.has_value and self.m1.value == 0) or \
               (self.m2.has_value and self.m2.value == 0):
            self.product.set_value(0, self)
        elif self.m1.has_value and self.m2.has_value:
            self.product.set_value(self.m1.value * self.m2.value, self)
        elif self.m1.has_value and self.product.has_value:
            self.m2.set_value(self.product.value / self.m1.value, self)
        elif self.m2.has_value and self.product.has_value:
            self.m1.set_value(self.product.value / self.m2.value, self)

    def process_forget_value(self):
        self.product.forget_value(self)
        self.m1.forget_value(self)
        self.m2.forget_value(self)
        self.process_new_value()
    def __str__(self):
        return '{0} * {1} = {2}'.format(
            self.m1.value, self.m2.value, self.s.value)


if __name__ == '__main__':
    a1 = Connector()
    a2 = Connector()
    s = Connector()
    adder = Adder(a1, a2, s)
    i = 'kamimura'
    a1.probe('a1')
    a2.probe('a2')
    s.probe('sum')
    try:
        a1.set_value(10, i)
        a2.set_value(20, i)
        a1.forget_value(i)
        print(adder)
        a1.set_value(100, i)
        print(adder)
        s.set_value(100, i)
        s.set_value(200, i)
    except Exception as err:
        print(err)

    c = Connector()
    f = c.celsius_fahrenheit_converter()
    c.probe('celsius')
    f.probe('fahrenheit')
    f.set_value(32, i)
    f.forget_value(i)
    c.set_value(20, i)
