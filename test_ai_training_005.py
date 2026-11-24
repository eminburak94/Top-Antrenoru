import unittest
from unittest.mock import patch
from oyuncu import prepare_player

class AITrainingTests(unittest.TestCase):
    def run_case(self, age=20, injury=0, returning=0, team='AI', programme='General'):
        s=dict(year=2000, week=1, club='USER', employed=True)
        p={'id':'test'}
        z=dict(condition=80, morale=70, injury=injury, return_weeks=returning)
        with patch('oyuncu.state', return_value=z), patch('oyuncu.age_at', return_value=age):
            prepare_player(s,p,team,0,programme)
            first=z.get('training_weeks',0)
            if team=='AI':
                prepare_player(s,p,team,0,programme)
                self.assertEqual(z.get('training_weeks',0),first)
                s['week']+=1
                prepare_player(s,p,team,0,programme)
                self.assertEqual(z.get('training_weeks',0),first*2)
        return first
    def test_healthy_ai(self): self.assertEqual(self.run_case(),.75)
    def test_injured(self): self.assertEqual(self.run_case(injury=1),0)
    def test_age_boundary(self): self.assertEqual(self.run_case(age=25),0)
    def test_returning(self): self.assertEqual(self.run_case(returning=1),0)
    def test_user_general(self): self.assertEqual(self.run_case(team='USER'),0)
    def test_user_development(self): self.assertEqual(self.run_case(team='USER',programme='Development'),1)

if __name__=='__main__': unittest.main()
