import tempfile,unittest
from pathlib import Path
import pandas as pd
from sp500_lakehouse.feature_checkpoints import checkpoint_identity,save_checkpoint,load_checkpoint

class FeatureCheckpointTests(unittest.TestCase):
    def test_content_verified_restart_and_corruption_gate(self):
        with tempfile.TemporaryDirectory() as root:
            class Config:
                def volume(self,name):return root
            cfg=Config();identity=checkpoint_identity({'capture':'x','code':'y'})
            frame=pd.DataFrame(dict(security_id=['a'],date=pd.to_datetime(['2026-10-30']),value=[1.5]))
            frames=dict(technical=frame,_canonical_financial={'income':frame})
            manifest=save_checkpoint(cfg,identity,frames,{'passed':True})
            restored,proof=load_checkpoint(cfg,identity)
            pd.testing.assert_frame_equal(restored['technical'],frame,check_dtype=False)
            self.assertEqual(proof,{'passed':True})
            self.assertEqual(save_checkpoint(cfg,identity,frames,proof),manifest)
            (Path(manifest).parent/'technical.parquet').write_bytes(b'corrupt')
            with self.assertRaises(ValueError):load_checkpoint(cfg,identity)
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):load_checkpoint(None,'../outside')

if __name__=='__main__':unittest.main()
