def validSequence(word1: str, word2: str):
    result = []
    def helper(ind1, ind2, remain, prank):
        if ind2 >= len(word2) or ind1 >= len(word1):
            if len(prank) == len(word2):
                result.append(prank)
            return
        if remain < 0:
            return
        left, right = '', ''
        if word1[ind1] == word2[ind2]:
            left = helper(ind1 + 1, ind2 + 1, remain,  prank + str(ind1))
        else:
            if remain !=0:
                left = helper(ind1 + 1, ind2 + 1, remain - 1, prank + str(ind1))
        right = helper(ind1 + 1, ind2, remain, prank) 
        
        

    helper(0, 0, 1, '')
    if len(result) == 0:
        return []
    return [int(i) for i in min(result)]

print(validSequence("abc", 'abd'))