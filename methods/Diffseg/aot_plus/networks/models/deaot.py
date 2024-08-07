import torch
import torch.nn as nn

from networks.layers.transformer import DualBranchGPM
from networks.models.aot import AOT
from networks.decoders import build_decoder
from timm.models.layers import trunc_normal_


class DeAOT(AOT):
    def __init__(self, cfg, encoder='mobilenetv2', decoder='fpn'):
        super().__init__(cfg, encoder, decoder)

        self.LSTT = DualBranchGPM(
            cfg.MODEL_LSTT_NUM,
            cfg.MODEL_ENCODER_EMBEDDING_DIM,
            cfg.MODEL_SELF_HEADS,
            cfg.MODEL_ATT_HEADS,
            emb_dropout=cfg.TRAIN_LSTT_EMB_DROPOUT,
            droppath=cfg.TRAIN_LSTT_DROPPATH,
            lt_dropout=cfg.TRAIN_LSTT_LT_DROPOUT,
            st_dropout=cfg.TRAIN_LSTT_ST_DROPOUT,
            droppath_lst=cfg.TRAIN_LSTT_DROPPATH_LST,
            droppath_scaling=cfg.TRAIN_LSTT_DROPPATH_SCALING,
            intermediate_norm=cfg.MODEL_DECODER_INTERMEDIATE_LSTT,
            return_intermediate=True)

        decoder_indim = cfg.MODEL_ENCODER_EMBEDDING_DIM * \
            (cfg.MODEL_LSTT_NUM * 2 +
             1) if cfg.MODEL_DECODER_INTERMEDIATE_LSTT else cfg.MODEL_ENCODER_EMBEDDING_DIM * 2


        if self.decoder_name == "diffuison":
            self.decoder = build_decoder(
                decoder,
                in_dim=decoder_indim,
                out_dim=cfg.MODEL_MAX_OBJ_NUM + 1,
                decode_intermediate_input=cfg.MODEL_DECODER_INTERMEDIATE_LSTT,
                hidden_dim=cfg.MODEL_ENCODER_EMBEDDING_DIM,
                shortcut_dims=cfg.MODEL_ENCODER_DIM,
                align_corners=cfg.MODEL_ALIGN_CORNERS,
                # Add
                schedule= cfg.MODEL_DECODER_SCHEDULE,
                model= cfg.MODEL_DECODER_DIFF_MODEL,
                timestep = cfg.MODEL_DECODER_TIMESTEP, 
                condition_dim = cfg.MODEL_CONDITION_DIM,
                generate_seed = cfg.MODEL_DECODER_GENERATE_SEED,
                guidance_scale = cfg.MODEL_DECODER_GUIDANCE_SCALE
            )
        else:

            self.decoder = build_decoder(
                decoder,
                in_dim=decoder_indim,
                out_dim=cfg.MODEL_MAX_OBJ_NUM + 1,
                decode_intermediate_input=cfg.MODEL_DECODER_INTERMEDIATE_LSTT,
                hidden_dim=cfg.MODEL_ENCODER_EMBEDDING_DIM,
                shortcut_dims=cfg.MODEL_ENCODER_DIM,
            )

        self.id_norm = nn.LayerNorm(cfg.MODEL_ENCODER_EMBEDDING_DIM)

        self._init_weight()

        self.use_temporal_pe = cfg.USE_TEMPORAL_POSITIONAL_EMBEDDING
        if self.cfg.USE_TEMPORAL_POSITIONAL_EMBEDDING:
            self.cur_pos_emb = nn.Parameter(torch.randn(1, cfg.MODEL_ENCODER_EMBEDDING_DIM //2) * 0.05)
            if self.cfg.TEMPORAL_POSITIONAL_EMBEDDING_SLOT_4:
                self.mem_pos_emb = nn.Parameter(torch.randn(4, cfg.MODEL_ENCODER_EMBEDDING_DIM //2) * 0.05)
            else:
                self.mem_pos_emb = nn.Parameter(torch.randn(2, cfg.MODEL_ENCODER_EMBEDDING_DIM //2) * 0.05)
            trunc_normal_(self.cur_pos_emb, std=.05)
            trunc_normal_(self.mem_pos_emb, std=.05)
        else:
            self.temporal_encoding = None

    def decode_id_logits(self, lstt_emb, shortcuts, gt_mask=None):

        n, c, h, w = shortcuts[-1].size()
        decoder_inputs = [shortcuts[-1]]
        for emb in lstt_emb:
            decoder_inputs.append(emb.view(h, w, n, -1).permute(2, 3, 0, 1))
        
        if self.decoder_name == "diffusion":
            with torch.no_grad():
                pred_logit = self.decoder.inference(decoder_inputs, shortcuts)
            if self.cfg.SPLIT == "train" and gt_mask != None:
                diffusion_loss = self.decoder.Diffusion_train(decoder_inputs, shortcuts, gt_mask)  
            else:
                diffusion_loss = None
            return diffusion_loss,  pred_logit

        elif  self.decoder_name == "fpn":
            pred_logit = self.decoder(decoder_inputs, shortcuts)
            return pred_logit
        else:
            raise NotImplementedError

    def get_id_emb(self, x):
        id_emb = self.patch_wise_id_bank(x)
        id_emb = self.id_norm(id_emb.permute(2, 3, 0, 1)).permute(2, 3, 0, 1)
        id_emb = self.id_dropout(id_emb)
        return id_emb
