'''
This file helps when trying to track the max value of a number.
'''


class Maximizer():
    '''
    This is a simple class to create an object that can easily be
    updated if the new value is greater than existing.
    '''
    current_value = 0

    def update(self, new_value):
        '''
        This function updates the current value if the new value is greater.
        '''
        if new_value > self.current_value:
            self.current_value = new_value

    def get(self):
        '''
        This function gets the current value.
        '''
        return self.current_value
